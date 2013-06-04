In order to run these tests you'll need to get a classpath for Jython to use:

To get the class path: 
* In the base redbox directory run: mvn dependency:build-classpath -Dmdep.cpFile=classpath
* Copy the classpath back to this test directory and `jython <script>` should now work.

You may also need the mock library - try to run the tests first though:
  1.  Install setuptools: http://www.jython.org/jythonbook/en/1.0/appendixA.html#setuptools
  1.  Install mock: http://www.voidspace.org.uk/python/mock/#installing

Make sure you use the Jython easy install (might be something like sudo /opt/local/share/java/jython/bin/easy_install -U mock)

TO RUN THE TESTS:
  * `jython AlertsTestData.py`
  
TO TEST YOUR OWN Alert CONFIG
  * `jython alert_test.py <config file>`
  
  
You can try out alert_test by 
 * `cd to config/src/main/config/portal/default/redbox/scripts/hkjobs/new-alerts/alertlib/test`
 * `cp -r config/test-alerts ./`
 * `jython alert_test.py config/system-config-new.json`

The result of the test can be found in `test-alerts/config-new/.processed/`
  
These tests stub the interaction with ReDBox (HarvesterClient) so won't actually upload the metadata into the system.
