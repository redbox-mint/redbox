/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.googlecode.fascinator.redbox;

/**
 *
 * @author lucido
 */
public class CacheEntry {

    private boolean allowed;
    private long lastUpdated;

    public CacheEntry() {
        setLastUpdated(System.currentTimeMillis());
    }

    public boolean isAllowed() {
        return allowed;
    }

    public void setAllowed(boolean allowed) {
        this.allowed = allowed;
    }

    public long getLastUpdated() {
        return lastUpdated;
    }

    public void setLastUpdated(long lastUpdated) {
        this.lastUpdated = lastUpdated;
    }
}
