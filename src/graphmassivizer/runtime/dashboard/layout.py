import sys
sys.path.insert(0, '/home/haleh/PycharmProjects/architecture-stubs/src')
from dash import html, dash_table, dcc, Input, Output, State
#import dash_cytoscape as cyto
import networkx as nx
from config import add_node_btn, bgo_dag_nx_graph, df_computing_nodes


def get_layout(containers_info_df):
    return html.Div([    
    # Controls    
    html.H1("Simulation"),
    html.Button("Update containers", id="updt-containers-btn", n_clicks=0, style={"marginTop": "10px"}),
    html.H1("Editable DataFrame Table", style={"textAlign": "center"}),
    dash_table.DataTable(
        id='computing-nodes-table',
        columns=[{"name": col, "id": col, "editable": True} for col in containers_info_df.columns],
        data=containers_info_df.to_dict('records'),
        editable=True,
        row_deletable=True,
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'center',
            'padding': '10px',
            'border': '1px solid black'
        }
    ),
])
