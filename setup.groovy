String projectHome = project.properties["project.home"];
if (projectHome == null) {
    projectHome = project.basedir.parentFile.absolutePath;
    projectHome = projectHome.replace("\\", "/");
    project.properties["project.home"] = projectHome;
}
println "Project will be deployed to: " + projectHome;
