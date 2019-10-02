import sys
import re
import numpy as np
import copy
from decimal import *

# YOUR CODE GOES HERE

streets = []
getcontext().prec = 2


def parseCommand(userintemp):
    userin = userintemp.strip(" ")
    if userin[0] == "a":
        return "add"
    elif userin[0] == "c":
        return "change"
    elif userin[0] == "r":
        return "remove"
    elif userin[0] == "g":
        return "graph"
    else:
        return None

def parseStreetName(userintemp):
    userin = userintemp.strip(" ")
    streetname = re.search(r'\"[a-zA-Z\s]+\"', userin)
    return streetname.group()



def parseCoordinates(userintemp):
    userin = userintemp.strip(" ")
    coordinates = re.findall(r'(\(\s*-?[0-9]+\s*,\s*-?[0-9]+\s*\))', userin)
    coordinates = [coordinate.replace(" ", "") for coordinate in coordinates]
    return coordinates

def parseIntCoordinates(point):
    coordinates = re.findall(r'(-?[0-9]+)', point)
    return int(coordinates[0]), int(coordinates[1])


def checkFormat(userintemp):
    userin = userintemp.strip(" ")
    if userin[0] == "a" or userin[0] == "c":
        pattern = "[ac]\s+\"[a-zA-Z\s]+\"\s+(\(\s*-?[0-9]+\s*,\s*-?[0-9]+\s*\)\s*){2,}\n*"
        if re.match(pattern, userin) is not None:
            return True
    if userin[0] == "r":
        pattern = '(^r\s+)(\"[a-zA-Z\s]+\"\n*){1}'
        if re.match(pattern, userin) is not None:
            return True
    if userin[0] == "g":
        pattern = "((^g$\s+)\n*)"
        if re.match(pattern, userin) is not None:
            return True

    return False

def calculateIntersection(l1, l2):

    xdiff = (l1.endpoint1[0]-l1.endpoint2[0], l2.endpoint1[0]-l2.endpoint2[0])
    ydiff = (l1.endpoint1[1]-l1.endpoint2[1], l2.endpoint1[1]-l2.endpoint2[1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return None

    d = (det(l1.endpoint1, l1.endpoint2), det(l2.endpoint1, l2.endpoint2))
    x = round(float(det(d, xdiff) / div),2)
    y = round(float(det(d, ydiff) / div),2)

    if x in l2.xrange and y in l2.yrange and x in l1.xrange and y in l1.yrange:
        return (x, y)
    return None

def calculateVertices(streets):
    vertices = []
    length = len(streets)
    type = []
    vertStreets = []
    intercepts = []

    verticesdict = {}

    for i in range(length):

       # if i != 0:
       #     streetsToSearch = streets[0:i] + streets[i+1:length]
       # else:'''
        streetsToSearch = streets[i+1:length]


        for line in streets[i].lines:
            for street in streetsToSearch:
                for lineCompare in street.lines: #comparing each line in both sets of streets
                    if line == lineCompare: #if the two line segements are equal
                        if line.endpoint1 in vertices: #this sequence checks whether any of the endpoints are in the vertices list, and if they are endpoint vertices, it removes them
                            tempindex = vertices.index(line.endpoint1)
                            if type[tempindex] == "e":
                                del vertices[tempindex]
                                del type[tempindex]
                                del vertStreets[tempindex]
                        if line.endpoint2 in vertices:
                            tempindex = vertices.index(line.endpoint2)
                            if type[tempindex] == "e":
                                del vertices[tempindex]
                                del type[tempindex]
                                del vertStreets[tempindex]
                        if lineCompare.endpoint1 in vertices:
                            tempindex = vertices.index(lineCompare.endpoint1)
                            if type[tempindex] == "e":
                                del vertices[tempindex]
                                del type[tempindex]
                                del vertStreets[tempindex]
                        if lineCompare.endpoint2 in vertices:
                            tempindex = vertices.index(lineCompare.endpoint2)
                            if type[tempindex] == "e":
                                del vertices[tempindex]
                                del type[tempindex]
                                del vertStreets[tempindex]
                        continue

                    elif line.contains(lineCompare):
                        if lineCompare.endpoint1 not in intercepts:
                            intercepts.append(lineCompare.endpoint1)
                            if lineCompare.endpoint1 in vertices:
                                tempindex = vertices.index(lineCompare.endpoint1)
                                if type[tempindex] != "i":
                                    type[tempindex] = "i"
                                if streets[i] not in vertStreets[tempindex] and street not in vertStreets[tempindex]:
                                    vertStreets[tempindex] = [streets[i], street]
                            else:
                                vertices.append(lineCompare.endpoint1)
                                type.append("i")
                                vertStreets.append([streets[i], street])

                            if lineCompare.endpoint2 in vertices:
                                tempindex = vertices.index(lineCompare.endpoint2)
                                if type[tempindex] != "i":
                                    type[tempindex] = "i"
                                if streets[i] not in vertStreets[tempindex] and street not in vertStreets[tempindex]:
                                    vertStreets[tempindex] = [streets[i], street]
                            else:
                                vertices.append(lineCompare.endpoint2)
                                type.append("i")
                                vertStreets.append([streets[i], street])

                            if line.endpoint1 not in vertices and line.endpoint1 not in intercepts:
                                vertices.append(line.endpoint1)
                                type.append("e")
                                vertStreets.append(streets[i])

                            if line.endpoint2 not in vertices and line.endpoint1 not in intercepts:
                                vertices.append(line.endpoint2)
                                type.append("e")
                                vertStreets.append(streets[i])
                        continue

                    intersect = calculateIntersection(line, lineCompare) #calculate intersect of two lines
                    if intersect is not None: #append intersect and endpoints to the vertices list
                        if intersect not in intercepts:
                            intercepts.append(intersect)
                        if intersect in vertices: #if it's alreayd in the list, if it's listed as an endpoint type, change it to intersection, and adjust the streets list to reflect both streets
                            tempindex = vertices.index(intersect)
                            if type[tempindex] != "i":
                                type[tempindex] = "i"
                            if streets[i] not in vertStreets[tempindex] and street not in vertStreets[tempindex]:
                                vertStreets[tempindex] = [streets[i], street]
                            if lineCompare in streets[i].lines and line in street.lines:
                                del vertices[tempindex]
                                del type[tempindex]
                                del vertStreets[tempindex]

                        elif intersect not in vertices and (lineCompare not in streets[i].lines or line not in street.lines): #if the intersect is not in the list, and the two line segments being compared aren't on two streets at the same time
                            vertices.append(intersect)
                            type.append("i")
                            vertStreets.append([streets[i], street])

                        if line.endpoint1 not in vertices and intersect != line.endpoint1 and line.endpoint1 not in intercepts:
                            vertices.append(line.endpoint1)
                            type.append("e")
                            vertStreets.append([streets[i]])
                        if line.endpoint2 not in vertices and intersect != line.endpoint2 and line.endpoint2 not in intercepts:
                            vertices.append(line.endpoint2)
                            type.append("e")
                            vertStreets.append([streets[i]])
                        if lineCompare.endpoint1 not in vertices and lineCompare.endpoint1 != intersect and lineCompare.endpoint1 not in intercepts:
                            vertices.append(lineCompare.endpoint1)
                            type.append("e")
                            vertStreets.append([street])
                        if (lineCompare.endpoint2) not in vertices and lineCompare.endpoint2 != intersect and lineCompare.endpoint2 not in intercepts:
                            vertices.append(lineCompare.endpoint2)
                            type.append("e")
                            vertStreets.append([street])


    verticesClassList =  []

    for i in range(len(vertices)): #create a list of vertices using the Vertex Class
        verticesClassList.append(Vertex(vertices[i], type[i], vertStreets[i]))

    for i in range(len(verticesClassList)): #make a dict with vertex IDs
        verticesdict.update({i+1:verticesClassList[i]})

    return verticesdict

def calculateEdges(verticesdict):
    edges = []
    vertices = []

    for key, value in verticesdict.iteritems():
        vertices.append((key, value))

    length = len(vertices)

    for i in range(length):
        verticesToSearch = vertices[i+1:]

        vertex1 = vertices[i]

        for street1 in vertex1[1].streets: #loops through all streets listed in first vertex
            for vertex2 in verticesToSearch: #check which line seg the vertices are on, as well as the type
                vertex1Check = vertexCheck(vertex1[1], street1)
                vertex2Check = vertexCheck(vertex2[1], street1)

                if vertex1Check is not None and vertex2Check is not None:
                    if vertex1[1].type == "i" or vertex2[1].type == "i": #if at least one is an intersect
                        if checkPath(vertex1[1], vertex2[1], vertex1Check, vertex2Check, vertices, street1) and (vertex1[0], vertex2[0]) not in edges and (vertex2[0], vertex1[0]) not in edges: #if the path to the 2nd vertex is clear
                            edges.append((vertex1[0], vertex2[0]))

                for street2 in vertex2[1].streets: #as above, but repeated for 2nd vertex
                    vertex1Check = vertexCheck(vertex1[1], street2)
                    vertex2Check = vertexCheck(vertex2[1], street2)

                    if vertex1Check is not None and vertex2Check is not None:

                        if vertex1[1].type == "i" or vertex2[1].type == "i":
                            if checkPath(vertex1[1], vertex2[1], vertex1Check, vertex2Check, vertices, street2)  and (vertex1[0], vertex2[0]) not in edges and (vertex2[0], vertex1[0]) not in edges:
                                edges.append((vertex1[0], vertex2[0]))
    return edges


def checkPath(vertex1, vertex2, vertex1Check, vertex2Check, vertices, streetToSearch):


    street = copy.deepcopy(streetToSearch)
    start = -1
    end = -1

    if vertex1Check[0] < vertex2Check[0]: #setting up path parameters
        start = vertex1Check[0]
        end = vertex2Check[0]+1
        if street.lines[start].endpoint2 == vertex1.coordinate:
            start += 1
        elif street.lines[start].endpoint1 != vertex1.coordinate and street.lines[start].endpoint2 != vertex1.coordinate:
            newLine = Line((int(vertex1.coordinate[0]), int(vertex1.coordinate[1])), street.lines[start].endpoint2)
            street.changeLine(start, newLine)

        if vertex2.coordinate == street.lines[end-1].endpoint1:
            end -= 1
        elif vertex2.coordinate != street.lines[end-1].endpoint2 and vertex2.coordinate != street.lines[end-1].endpoint1:
            newLine = Line(street.lines[end-1].endpoint1,(int(vertex2.coordinate[0]), int(vertex2.coordinate[1])))
            street.changeLine(end-1, newLine)

    elif vertex2Check[0] < vertex1Check[0]:
        start = vertex2Check[0]
        end = vertex1Check[0]+1

        if street.lines[start].endpoint2 == vertex2.coordinate:
            start += 1
        elif street.lines[start].endpoint1 != vertex2.coordinate and street.lines[start].endpoint2 != vertex2.coordinate:
            newLine = Line((int(vertex2.coordinate[0]), int(vertex2.coordinate[1])), street.lines[start].endpoint2)
            street.changeLine(start, newLine)

        if vertex1.coordinate == street.lines[end - 1].endpoint1:
            end -= 1
        elif vertex1.coordinate != street.lines[end-1].endpoint2 and vertex1.coordinate != street.lines[end - 1].endpoint1:
            newLine = Line(street.lines[end-1].endpoint1, (int(vertex1.coordinate[0]), int(vertex1.coordinate[1])))
            street.changeLine(end - 1, newLine)
    else:
        start = vertex2Check[0]
        end = vertex2Check[0]

    if start == end: #already checked that at least one is an intersection, so the other must be an endpoint. Make a new line segment between them, and then see if any other vertices pop up on that
        line = Line((int(vertex1.coordinate[0]),int(vertex1.coordinate[1])),(int(vertex2.coordinate[0]),int(vertex2.coordinate[1])))
        for vertex in vertices:
            if not vertex[1].equals(vertex1) and not vertex[1].equals(vertex2):
                if line.checkPointOnLine(vertex[1].coordinate):
                    return False

    else:
        for i in range(start,end):


            for vertex in vertices:
                if not vertex[1].equals(vertex1) and not vertex[1].equals(vertex2):
                    if street.lines[i].checkPointOnLine(vertex[1].coordinate):
                        return False

    return True

def vertexCheck(vertex, street): #checks which line segment of a street the vertex is on, and whether it's an endpoint on that segment
    lineseg = -1
    endpoint = -1

    for i in range(len(street.lines)):
        if street.lines[i].checkPointOnLine(vertex.coordinate):

            lineseg = i

            if vertex.coordinate == street.lines[i].endpoint1:
                endpoint = 1
            elif vertex.coordinate == street.lines[i].endpoint2:
                endpoint = 2


            return (lineseg, endpoint)

    return None

def produceStreet(streetname, coordinates):
    length = len(coordinates)
    street = None

    for i in range(length - 1):
        if i == 0:
            street = Street(Line(parseIntCoordinates(coordinates[i]), parseIntCoordinates(coordinates[i+1])), streetname)
        else:
            street.addLine(Line(parseIntCoordinates(coordinates[i]), parseIntCoordinates(coordinates[i+1])))

    return street





class Line:
    def __init__(self, p1, p2):
        self.x1 = float(p1[0])
        self.x2 = float(p2[0])
        self.y1 = float(p1[1])
        self.y2 = float(p2[1])
        self.endpoint1 = (self.x1, self.y1)
        self.endpoint2 = (self.x2, self.y2)

        if self.x2 >= self.x1:
            self.xrange = np.round(np.arange(self.x1, self.x2+0.01, 0.01),2)
        else:
            self.xrange = np.round(np.arange(self.x2, self.x1+0.01, 0.01),2)

        if self.y2 >= self.y1:
            self.yrange = np.round(np.arange(self.y1, self.y2+0.01, 0.01),2)
        else:
            self.yrange = np.round(np.arange(self.y2, self.y1+0.01, 0.01),2)

        if self.x1 == self.x2:
            self.m = None
            self.intercept = None
        else:
            self.m = round(float((self.y2 - self.y1)/(self.x2 - self.x1)),2)
            self.intercept = round(float(self.y1 - self.m*self.x1),2)

    def checkPointOnLine(self,p):
        if self.m is not None:
            ytemp = self.m * p[0] + self.intercept
            ytemp = Decimal(str(ytemp))
            py = Decimal(str(p[1]))

            if Decimal(ytemp).compare(py) == Decimal('0'): #this isn't working for some reason
                if p[1] in self.yrange:
                    if p[0] in self.xrange:
                        return True
        else:
            if p[0] == self.x1 and p[1] in self.yrange:
                return True


        return False

    def __eq__(self,l):
        if l.m == self.m and ((l.endpoint1[0] in self.xrange and l.endpoint1[1] in self.yrange and np.where(self.xrange == l.endpoint1[0]) == np.where(self.yrange == l.endpoint1[1])) and (l.endpoint2[0] in self.xrange and l.endpoint2[1] in self.yrange and np.where(self.xrange == l.endpoint2[0]) == np.where(self.yrange == l.endpoint2[1]))): #== self.endpoint1 or l.endpoint1 == self.endpoint2 or l.endpoint2 == self.endpoint2 or l.endpoint2 == self.endpoint1):#modify here... account for endpoints in x range or y range
            return True
        return False

    def contains(self,l):
        if l.m == self.m:
            if self.checkPointOnLine(l.endpoint1) or self.checkPointOnLine(l.endpoint2):
                return True

        return False

class Street:


    def __init__(self, l1, name):
        self.name = name
        self.lines = [l1]
        #self.vertices = {}

    def addLine(self,line):
        self.lines.append(line)

    def changeLine(self, lineSeg, newLine):
        self.lines[lineSeg] = newLine

    def __eq__(self, otherStreet):
        if self.name == otherStreet.name and self.lines == otherStreet.lines:
            return True
        return False

    

class Vertex:
    def __init__(self, coordinate, type, streets):
        self.coordinate = coordinate
        self.type = type
        self.streets = streets

    def equals(self,vertexCompare):
        if self.coordinate == vertexCompare.coordinate and self.type == vertexCompare.type and self.streets == vertexCompare.streets:
            return True
        return False

def main():
    ### YOUR MAIN CODE GOES HERE

    ### sample code to read from stdin.
    ### make sure to remove all spurious print statements as required
    ### by the assignment

    streets = []

    def produceGraph(streets):
        vertices = calculateVertices(streets)
        edges = calculateEdges(vertices)

        sys.stderr.write("V = {\n")

        for key, value in vertices.iteritems():
            sys.stderr.write("%d:\t(%.2f,%.2f)\n" % (key, value.coordinate[0], value.coordinate[1]))
        sys.stderr.write("}\n")
        sys.stderr.write("E = {\n")

        for edge in edges:
            sys.stderr.write("<%d,%d>\n" % (edge[0], edge[1]))
        sys.stderr.write("}\n")
    while True:
        line = sys.stdin.readline()
        if line == '':
            continue
        if checkFormat(line):
            command = parseCommand(line)
            if command == "add":
                streetname = parseStreetName(line).capitalize()
                coordinates = parseCoordinates(line)
                street = produceStreet(streetname, coordinates)
                if street in streets:
                    sys.stderr.write("Error: that street is already present. Please re-enter your command\n")
                    continue
                streets.append(street)
            elif command == "change":
                streetname = parseStreetName(line).capitalize()
                coordinates = parseCoordinates(line)
                presence = False
                street = produceStreet(streetname, coordinates)
                for i in range(len(streets)):
                    if streets[i].name == streetname:
                        presence = True
                        streets[i] = street
                if not presence:
                    sys.stderr.write("Error: that street has not yet been added. Please re-enter your command\n")
                    continue
            elif command == "remove":
                streetname = parseStreetName(line).capitalize()
                y = -1
                for i in range(len(streets)):
                    if streets[i].name == streetname:
                        y = i
                if y > -1:
                    del streets[y]
                else:
                    sys.stderr.write("Error: that street has not yet been added. Please re-enter your command\n")
                    continue
            else:
                produceGraph(streets)

        else:
            sys.stderr.write("Error: incorrect format. Please try again\n")
            continue




    #print 'Finished reading input'
    # return exit code 0 on successful termination
    sys.exit(0)




if __name__ == '__main__':
    main()
