from utils import *

def polygen_plot(P: Polygon, ocol="k-", show=True):
    for (p1, p2) in P.E:
        plt.plot([p1.x, p2.x], [p1.y, p2.y], ocol)
    if show:
        plt.show()

def polygens_plot(T: set[Polygon], show=False):
    for poly in T:
        polygen_plot(poly, show=False)

class Kirkpatrick:
    def __init__(self) -> None:
        self.previous = Polygon((-200, -200), (-300, -301), (-301, -300))
        self.parent = dict()
        self.adj = dict()
        self.nodes = set()
        self.polygons = list()
        self.user_map = dict()
        self.user_input = dict()
        self.delaunay = set()
        self.super_triangle = Polygon((150, 0),(-150, 150),(-150, -150))
    
    def add_region(self, poly: Polygon, name: str):
        self.user_input[poly] = name
        self.polygons.append(poly)
    
    def add_node(self, poly: Polygon):
        self.nodes.add(poly) 
        self.adj[poly] = []

    def retriangulate(self, poly: Polygon):
        triangulations = set()
        vertices = [v for v in poly.V]
        triangles_found = -1
        while (triangles_found != 0):
            triangles_found = 0
            for index, vertex in enumerate(vertices):
                next = vertices[(index+1)%len(vertices)]
                prev = vertices[index-1]

                v1 = next-vertex
                v2 = prev-vertex

                if (v1.x*v2.y - v1.y*v2.x > 0):
                    ccw_vertices = getcommon([vertex, prev, next])
                    T = Polygon(*ccw_vertices)
                    inside = [point_in_triangle(v, T) for v in vertices]
                    if inside.count(True) > 3:
                        continue
                    else:
                        vertices.pop(index)
                        triangulations.add(T)
                        triangles_found+=1
        
        return triangulations

    def triangulate_helper(self, polys: list[Polygon]):
        super_t = self.super_triangle
        triangulations = set([super_t])

        for poly in polys:
            vertices = poly.V
            print(f"Vertices : {vertices}")
            for vertex in vertices:    
                bad_triangles = []
                for tpoly in triangulations:
                    if (is_inside(vertex, tpoly)):
                        bad_triangles.append(tpoly) 

                edges = []
                for tri in bad_triangles:
                    for edge in tri.E:
                        temp_e = edge
                        if (temp_e[0].x == temp_e[1].x):
                            if (temp_e[1].y < temp_e[0].y): temp_e = (temp_e[1], temp_e[0])
                        elif (temp_e[1].x < temp_e[0].x):
                            temp_e = (temp_e[1], temp_e[0])
                        edges.append(temp_e)
                
                p_set = filter(lambda x: edges.count(x) == 1, edges)
            
                for bpoly in bad_triangles:
                    triangulations.remove(bpoly)
                
                for edge in p_set:
                    [x, y, z] = getcommon([edge[0], edge[1], vertex])
                    triangulations.add(Polygon(x, y, z))

        return triangulations

    def triangulate(self):
        triangulations = self.triangulate_helper(self.polygons)

        for poly in self.polygons:
            for tri in triangulations:
                vertices = tri.V
                flag = True
                for vertex in vertices:
                    if vertex not in poly.V: 
                        flag = False
                        break
                if flag: self.user_map[tri] = poly
        for tri in triangulations:
            self.nodes.add(tri)
            self.adj[tri] = []
        
        self.delaunay = triangulations
    
    def remove_point(self, p: Point):
        removed_triangles = set()
        for tri in self.delaunay:
            if p in tri.V: removed_triangles.add(tri)

        v_set = set()
        for tri in removed_triangles:
            for v in tri.V:
                v_set.add(v)
            self.delaunay.remove(tri)

        v_set.remove(p)
        v_list = getcommon(list(v_set), p)
        
        print("Independent points : ",v_list)

        new_triangles = self.retriangulate(Polygon(*v_list))

        for tri in new_triangles: 
            self.delaunay.add(tri)
            self.add_node(tri)
        for old in removed_triangles:
            self.parent[old] = []

        for new in new_triangles:
            for old in removed_triangles:
                # if triangle_overlap(new, old):
                self.adj[new].append(old)
                self.parent[old].append(new)

    def select_independent_set(self):
        all_vertices = {vertex for tri in self.delaunay for vertex in tri.V}
        ind_set = set()
        marked_set = {vertex for vertex in self.super_triangle.V}

        for vertex in all_vertices:
            if vertex in marked_set:
                continue
            ind_set.add(vertex)
            marked_set.add(vertex)
            for tri in self.delaunay:
                if vertex in tri.V:
                    for _vertex in tri.V: 
                        marked_set.add(_vertex)
        #print(ind_set)
        return ind_set


    def search_point(self, p: Point,triangulations):
        if not point_in_triangle(p, self.super_triangle):
            return "External Region"

        cur = None
        index = 0

        def plot_util(p:Point):
            nonlocal index
            plt.plot(p.x, p.y, 'ro')
            polygen_plot(self.super_triangle, 'b-', show=False)
            polygen_plot(triangle, 'r-', show=True)
            index+=1
        
        if self.previous != Polygon((-200, -200), (-300, -301), (-301, -300)) and point_in_triangle(p, self.previous):
            for triangle in self.parent[self.previous]:
                for t in self.adj[triangle]:
                    if point_in_triangle(p, t):
                        print("Found using parent of previous search!")
                        plot_util(p)

                        cur = triangle
                        return self.user_input.get(self.user_map[self.previous], "External Region")
                        # break
        for triangle in self.delaunay:
            if point_in_triangle(p, triangle):
                cur = triangle

                plot_util(p)

                break
    
        while self.adj[cur] != []:
            for triangle in self.adj[cur]:
                if point_in_triangle(p, triangle):
                    plot_util(p)

                    cur = triangle
                    
                    break
        
        plt.plot(p.x,p.y,'ro') 
        polygens_plot(triangulations[-1])

        if cur in self.user_map:
            self.previous = cur
            cur = self.user_map[cur]
            polygen_plot(cur, 'g-', show = False)
        plt.show()
        
        #print("ANSWER IS", cur)

        return self.user_input.get(cur, "External Region")
