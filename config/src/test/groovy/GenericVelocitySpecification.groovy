import org.apache.velocity.Template
import org.apache.velocity.VelocityContext
import org.apache.velocity.app.Velocity
import org.apache.velocity.app.VelocityEngine
import spock.lang.Shared
import spock.lang.Specification
import spock.lang.Unroll

/*
 *
 *  Copyright (C) 2016 Queensland Cyber Infrastructure Foundation (http://www.qcif.edu.au/)
 *
 *    This program is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation; either version 2 of the License, or
 *    (at your option) any later version.
 *
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License along
 *    with this program; if not, write to the Free Software Foundation, Inc.,
 *    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 * /
 */

/**
 * @author <a href="matt@redboxresearchdata.com.au">Matt Mulholland</a>
 * Created on 22/10/2016.
 */
abstract class GenericVelocitySpecification extends Specification{
    @Shared VelocityEngine velocityEngine
    @Shared Template velocityTemplate
    @Shared VelocityContext velocityContext

    def setupSpec() {
        def absolutePath = new File(getClass().getResource("/").toURI()).getPath()
        velocityEngine = new VelocityEngine()
        velocityEngine.setProperty(Velocity.FILE_RESOURCE_LOADER_PATH, absolutePath)
        velocityEngine.init()
    }

    def setup() {
        velocityContext = new VelocityContext()
    }

    def initTemplate(String templateName) {
        velocityTemplate = velocityEngine.getTemplate(templateName)
    }

}
