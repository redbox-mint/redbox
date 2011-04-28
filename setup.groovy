String projectHome = project.properties["project.home"];
if (projectHome == null) {
    projectHome = project.basedir.parentFile.absolutePath;
    projectHome = projectHome.replace("\\", "/");
    project.properties["project.home"] = projectHome;
}
println "Project will be deployed to: " + projectHome;

java.net.InetAddress address = InetAddress.getByName(System.getenv("COMPUTERNAME"));
project.properties["ip.address"] = address.getHostAddress();
println "Computer IP Address: " + project.properties["ip.address"];