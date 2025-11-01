"""
人物关系图谱可视化工具
"""

import json
from typing import Dict, List

def visualize_ascii(graph: RelationGraph):
    entities = graph.get_all_entities()
    
    for entity in entities:
        relations = graph.get_relations(entity)
        if not relations:
            continue
        
        print(f"┌─ {entity}")
        for i, (rel_type, targets) in enumerate(relations.items()):
            is_last = (i == len(relations) - 1)
            prefix = "└─" if is_last else "├─"
            
            for j, target in enumerate(targets):
                is_last_target = (j == len(targets) - 1)
                if j == 0:
                    print(f"│  {prefix} [{rel_type}] → {target}")
                else:
                    continuation = "   " if is_last else "│  "
                    print(f"│  {continuation}              └─ {target}")
        print("│")
    
    print("=" * 60 + "\n")

def save_graphviz(graph: RelationGraph, output_file: str = "relation_graph.png"):
    """
    使用 Graphviz 生成关系图谱图片
    """
    try:
        from graphviz import Digraph
    except ImportError:
        print("Graphviz not installed. Install with: pip install graphviz")
        return
    
    dot = Digraph(comment='人物关系图谱')
    dot.attr(rankdir='LR') 
    dot.attr('node', shape='circle', style='filled', fillcolor='lightblue')
    
    entities = graph.get_all_entities()
    for entity in entities:
        dot.node(entity, entity)
    
    for head in graph.graph:
        for relation in graph.graph[head]:
            for tail in graph.graph[head][relation]:
                dot.edge(head, tail, label=relation)
    
    dot.render(output_file.replace('.png', ''), format='png', cleanup=True)

def generate_html_visualization(graph: RelationGraph, output_file: str = "relation_graph.html"):
    """
    生成交互式网页可视化（使用 Cytoscape.js）
    """
    cytoscape_data = graph.export_cytoscape()
    
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>人物关系图谱</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.23.0/cytoscape.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        #cy {
            width: 100%;
            height: 600px;
            border: 2px solid #ddd;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .info {
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .legend {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 10px;
        }
        .legend-item {
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>人物关系图谱</h1>

    <div id="cy"></div>

    <script>
        var cy = cytoscape({
            container: document.getElementById('cy'),
            
            elements: """ + json.dumps(cytoscape_data, ensure_ascii=False) + """,
            
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#69b3a2',
                        'label': 'data(label)',
                        'color': '#fff',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-size': '12px',
                        'width': 60,
                        'height': 60,
                        'border-width': 2,
                        'border-color': '#4a7c8a'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#ccc',
                        'target-arrow-color': '#ccc',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '10px',
                        'text-rotation': 'autorotate',
                        'text-margin-y': -10
                    }
                },
                {
                    selector: 'node:selected',
                    style: {
                        'background-color': '#ff6b6b',
                        'border-width': 4
                    }
                },
                {
                    selector: 'edge:selected',
                    style: {
                        'line-color': '#ff6b6b',
                        'target-arrow-color': '#ff6b6b',
                        'width': 4
                    }
                }
            ],
            
            layout: {
                name: 'cose',  // 力导向布局
                animate: true,
                animationDuration: 500,
                nodeRepulsion: 8000,
                idealEdgeLength: 100,
                edgeElasticity: 100,
                gravity: 1
            }
        });
        
        // 点击节点高亮相关边
        cy.on('tap', 'node', function(evt){
            var node = evt.target;
            var neighbors = node.neighborhood();
            
            cy.elements().style('opacity', 0.3);
            node.style('opacity', 1);
            neighbors.style('opacity', 1);
        });
        
        // 点击空白处恢复
        cy.on('tap', function(evt){
            if(evt.target === cy){
                cy.elements().style('opacity', 1);
            }
        });
    </script>
</body>
</html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)