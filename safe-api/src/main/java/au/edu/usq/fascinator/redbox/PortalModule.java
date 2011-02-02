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
package au.edu.usq.fascinator.redbox;

import au.edu.usq.fascinator.api.indexer.Indexer;
import au.edu.usq.fascinator.api.storage.Storage;
import au.edu.usq.fascinator.portal.JsonSessionState;
import au.edu.usq.fascinator.portal.services.PortalSecurityManager;
import java.lang.reflect.Method;
import org.apache.tapestry5.ioc.Invocation;
import org.apache.tapestry5.ioc.MethodAdvice;
import org.apache.tapestry5.ioc.MethodAdviceReceiver;
import org.apache.tapestry5.ioc.annotations.Match;
import org.apache.tapestry5.services.ApplicationStateManager;
import org.slf4j.Logger;

/**
 * Module to provide a safe Storage API for the Jython layer. The wrapper will
 * call the Indexer to check access to DigitalObjects and Payloads.
 *
 * @author Oliver Lucido
 */
public class PortalModule {

    @Match("ScriptingServices")
    public static void adviseSafe(final Logger log,
            final ApplicationStateManager appStateManager,
            final Indexer indexer,
            final PortalSecurityManager securityManager,
            MethodAdviceReceiver receiver) {
        final JsonSessionState sessionState =
                appStateManager.getIfExists(JsonSessionState.class);

        MethodAdvice advice = new MethodAdvice() {

            @Override
            public void advise(Invocation invocation) {
                invocation.proceed();
                Storage storage = (Storage) invocation.getResult();
                invocation.overrideResult(new SecureStorage(storage, indexer,
                        securityManager, sessionState));
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
}
