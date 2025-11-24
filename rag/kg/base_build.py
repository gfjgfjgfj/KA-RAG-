from abc import ABC, abstractmethod
from py2neo import Graph, Node


class Builder(ABC):

    def __init__(self, url: str, user: str, password: str):
        self.g = Graph(url, auth=(user, password))

    @abstractmethod
    def build(self):
        pass

    def test(self):
        return

    # label：标签，实体类别
    # nodes：具体实体名称列表
    # properties：实体属性
    def create_nodes(self, label, nodes, **properties):
        for node_name in nodes:
            node = Node(label, name=node_name, **properties)
            self.g.create(node)

    # label：标签，实体类别
    # nodes：具体实体名称
    # properties：实体属性
    def create_node(self, label, node, **properties):
        self.g.create(Node(label, name=node, **properties))


    # start_label：开始节点标签
    # end_label:目标节点标签
    # edges：边 [node1,node2]
    # rel_type：关系标签
    # rel_name：关系名称
    def create_relationships(self, start_label, end_label, edges, rel_type, rel_name) -> bool:
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_label, end_label, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                return True
            except Exception as e:
                print(e)
                return False

    def create_relationship(self, start_label, end_label, start_node, end_node, rel_type, rel_name) -> bool:
        query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
            start_label, end_label, start_node, end_node, rel_type, rel_name)
        try:
            self.g.run(query)
            return True
        except Exception as e:
            print(e)
            return False

    # label：节点标签
    # node：目标节点
    # properties：新增的属性
    def addProperties(self, label, node, **properties) -> bool:
        match_query = "MATCH (n:%s {name:'%s'}) RETURN n" % (label, node)
        result = self.g.run(match_query)
        data = result.data()
        if data is not None:
            if len(data) != 0:
                node = data[0]['n']
                for key, value in properties.items():
                    if node[key] is None:
                        node[key] = value
                        self.g.push(node)
            return True
        else:
            print("节点不存在")
            return False
