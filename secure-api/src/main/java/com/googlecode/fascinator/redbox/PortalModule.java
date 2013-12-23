/*
 * The Fascinator - ReDBox
 * Copyright (C) 2011 University of Southern Queensland
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */
package com.googlecode.fascinator.redbox;

import com.googlecode.fascinator.api.authentication.AuthenticationException;
import com.googlecode.fascinator.api.authentication.User;
import com.googlecode.fascinator.api.indexer.Indexer;
import com.googlecode.fascinator.api.indexer.SearchRequest;
import com.googlecode.fascinator.api.storage.Storage;
import com.googlecode.fascinator.portal.JsonSessionState;
import com.googlecode.fascinator.portal.services.PortalSecurityManager;

import java.io.OutputStream;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;

import org.apache.commons.lang.StringUtils;
import org.apache.tapestry5.ioc.Invocation;
import org.apache.tapestry5.ioc.MethodAdvice;
import org.apache.tapestry5.ioc.MethodAdviceReceiver;
import org.apache.tapestry5.ioc.annotations.Match;
import org.apache.tapestry5.services.ApplicationStateManager;
import org.apache.tapestry5.services.RequestGlobals;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Module to provide a safe Storage API for the Jython layer. The wrapper will
 * call the Indexer to check access to DigitalObjects and Payloads.
 *
 * Also intercepts Solr requests and secures them based on current user access.
 *
 * @author Oliver Lucido
 */
public class PortalModule {
	private static String GUEST_USER = "guest";
	private static String GUEST_ROLE = "guest";

    @SuppressWarnings("unused")
	private Logger log = LoggerFactory.getLogger(PortalModule.class);

    @Match("ScriptingServices")
    public static void adviseSafe(final Logger log,
            final ApplicationStateManager appStateManager,
            final Indexer indexer,
            final PortalSecurityManager securityManager,
            MethodAdviceReceiver receiver) {

        MethodAdvice advice = new MethodAdvice() {

            @Override
            public void advise(Invocation invocation) {
                invocation.proceed();
                Storage storage = (Storage) invocation.getResult();
                invocation.overrideResult(new SecureStorage(storage, indexer,
                        securityManager,
                        appStateManager.getIfExists(JsonSessionState.class)));
            }
        };

        try {
            Method method = receiver.getInterface().getMethod("getStorage",
                    new Class[]{});
            receiver.adviseMethod(method, advice);
        } catch (Exception e) {
            log.error("Failed to advise: {}", e.getMessage());
        }
    }

    @Match("Indexer")
    public static void adviseSafeIndexer(final Logger log,
            final ApplicationStateManager appStateManager,
            final RequestGlobals requestGlobals,
            final Indexer indexer,
            final PortalSecurityManager securityManager,
            MethodAdviceReceiver receiver) {

        MethodAdvice advice = new MethodAdvice() {

            @Override
            public void advise(Invocation invocation) {
                SearchRequest request = (SearchRequest) invocation.getParameter(0);
                boolean hasSecurityFilter = false;
                Set<String> fqList = request.getParams("fq");
                if (fqList != null) {
                    for (String fq : fqList) {
                        if (fq.contains("owner:") || fq.contains("security_filter:")
                                || fq.contains("security_exception:")
                                || fq.contains("workflow_security:")) {
                            hasSecurityFilter = true;
                            break;
                        }
                    }
                }
                if (!hasSecurityFilter) {
                    log.debug("Adding security to Solr request: {}", request);
                    JsonSessionState state = appStateManager.getIfExists(JsonSessionState.class);

                    String username = GUEST_USER;
                    List<String> rolesList = null;
                    if (state.containsKey("username")) {
                        username = state.get("username").toString();
                        String source = state.containsKey("source") ? state.get("source").toString() : "system";
                        try {
                            User user = securityManager.getUser(state, username, source);
                            rolesList = Arrays.asList(securityManager.getRolesList(state, user));
                        } catch (AuthenticationException ae) {
                            log.error("Failed to get user access, assuming guest access", ae);
                            rolesList = new ArrayList<String>();
                            rolesList.add(GUEST_ROLE);
                        }
                    } else {
                        rolesList = new ArrayList<String>();
                        rolesList.add(GUEST_ROLE);
                    }

                    request.addParam("fq", "owner:\"" + username
                            + "\" OR security_filter:("
                            + StringUtils.join(rolesList, " OR ") + ")");
                    invocation.override(0, request);
                }
                invocation.proceed();
            }
        };

        try {
            Method method = receiver.getInterface().getMethod("search",
                    new Class[]{SearchRequest.class, OutputStream.class});
            receiver.adviseMethod(method, advice);
        } catch (Exception e) {
            log.error("Failed to advise: {}", e.getMessage());
        }
    }
}
