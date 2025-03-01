# frontend/utils.py
import plotly.graph_objects as go
import numpy as np
import sys

sys.setrecursionlimit(100000)

def create_mindmap_figure(graph_data):
    """
    Create an interactive mind map visualization using Plotly with radial tree layout.
    
    Args:
        graph_data (dict): Dictionary containing nodes and edges data
        
    Returns:
        plotly.graph_objects.Figure: Interactive mind map figure
    """
    
    # Extract nodes and edges
    nodes = graph_data['nodes']
    edges = graph_data['edges']
    
    # Find root node and create node dictionary
    node_dict = {node['id']: node for node in nodes}
    edge_dict = {}
    for edge in edges:
        if edge['from'] not in edge_dict:
            edge_dict[edge['from']] = []
        edge_dict[edge['from']].append(edge['to'])
    
    # Create node positions using radial tree layout
    pos = {}
    def assign_positions(node_id, angle_range, level, parent_x=0, parent_y=0):
        start_angle, end_angle = angle_range
        children = edge_dict.get(node_id, [])
        radius = 1.5 * level
        
        # Position current node
        angle = (start_angle + end_angle) / 2
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        pos[node_id] = (x, y)
        
        # Position children
        if children:
            angle_step = (end_angle - start_angle) / len(children)
            for i, child in enumerate(children):
                child_start = start_angle + i * angle_step
                child_end = child_start + angle_step
                assign_positions(child, (child_start, child_end), level + 1, x, y)
    
    # Start layout from root node
    root_id = 'root'  # Assuming 'root' is always the root node
    assign_positions(root_id, (0, 2 * np.pi), 0)
    
    # Create edge traces
    edge_traces = []
    for edge in edges:
        x0, y0 = pos[edge['from']]
        x1, y1 = pos[edge['to']]
        
        # Create curved edges
        edge_trace = go.Scatter(
            x=[x0, x1],
            y=[y0, y1],  # Add slight curve
            line=dict(width=1, color='#888'),
        )
        edge_traces.append(edge_trace)
    
    # Create node traces
    node_x, node_y, node_text, node_colors = [], [], [], []
    for node_id, (x, y) in pos.items():
        node_x.append(x)
        node_y.append(y)
        node_text.append(node_dict[node_id]['label'])  # Use node labels
        node_colors.append('#ff7f0e' if node_id == 'root' else '#1f77b4')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(size=10, color=node_colors, line=dict(width=1, color="black")),
        text=node_text,
        textposition="top center"
    )
    
    # Create figure
    fig = go.Figure([*edge_traces, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    
    return fig
    
    # Create edge traces
    edge_traces = []
    for edge in edges:
        x0, y0 = pos[edge['from']]
        x1, y1 = pos[edge['to']]
        
        edge_trace = go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        edge_traces.append(edge_trace)
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    
    for node in nodes:
        x, y = pos[node['id']]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node['label'])
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="top center",
        marker=dict(
            size=20,
            color='#1f77b4',
            line_width=2
        )
    )
    
    # Create figure
    fig = go.Figure(
        data=[*edge_traces, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )
    
    # Update layout for better interactivity
    fig.update_layout(
        dragmode='pan',
        clickmode='event+select'
    )
    
    return fig