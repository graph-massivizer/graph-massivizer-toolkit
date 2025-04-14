import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import dash_cytoscape as cyto
import config
import plotly.colors as pc


def get_layout():
    # Sidebar Navigation
    sidebar = dbc.Col(
        [
            html.H2("Navigation", className="text-center text-white"),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink("Zookeeper Nodes", href="/", active="exact"),
                    dbc.NavLink("Containers Info", href="/containers", active="exact"),
                    dbc.NavLink("Running Applications", href='/applications', active='exact' )
                ],
                vertical=True,
                pills=True,
                className="flex-column",
            ),
        ],
        width=2,  # Sidebar takes 2 columns
        style={"backgroundColor": "#1e1e1e", "padding": "20px", "height": "100vh"},
    )

    # Main Content Layout (Empty placeholder, will be updated dynamically)
    content = dbc.Col(id="page-content", width=10, style={"padding": "20px"})

    # App Layout
    return dbc.Container(
        [
            dcc.Location(id="url", refresh=False), 
            dbc.Row(
                [
                    sidebar,
                    content,
                ],
                className="gx-0",  # Removes space between columns
            )
        ],
        fluid=True,
        style={"backgroundColor": "#121212", "color": "white"},
    )


def zookeeper_page(df_znodes_data, znodes_hierarchy_graph_elements):
    cytoscape_stylesheet = [
        {
            'selector': 'node',
            'style': {
                'label': 'data(label)',
                'font-size': '24px',
                'width': '150px',
                'height': '150px',
                'color': 'white',
                'background-color': '#0074D9',
                'text-valign': 'center',
                'text-halign': 'center',
                'border-width': '2px',
                'border-color': '#fff'
            }
        },
        {
            'selector': 'edge',
            'style': {
                'width': 2,
                'line-color': '#ccc',
                'target-arrow-color': '#ccc',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier'
            }
        }
    ]

    return html.Div([
        html.H1("Zookeeper Dashboard", className="text-center mb-4", style={'backgroundColor':'white'}),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Zookeeper Hierarchical Representation", style={'color': 'white'})),
                    dbc.CardBody([
                        dcc.Dropdown(
                            id='layout-selector',
                            options=[
                                {'label': 'Breadthfirst', 'value': 'breadthfirst'},
                                {'label': 'Circle', 'value': 'circle'},
                                {'label': 'Cose', 'value': 'cose'},
                                {'label': 'Grid', 'value': 'grid'}
                            ],
                            value='breadthfirst',
                            clearable=False
                        ),
                        cyto.Cytoscape(
                            id='cytoscape-graph',
                            layout={'name': 'breadthfirst', 'directed': True, 'orientation': 'vertical'},
                            style={'width': '100%', 'height': '500px', 'backgroundColor': '#1e1e1e'},
                            elements=znodes_hierarchy_graph_elements,
                            stylesheet=cytoscape_stylesheet
                        )
                    ])
                ], style={'backgroundColor': '#1e1e1e', 'color': 'white'})
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Znodes Information", style={'color': 'white'})),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id='znodes-info-table',
                            columns=[{"name": col, "id": col, "editable": True} for col in df_znodes_data.columns],
                            data=df_znodes_data.to_dict('records'),
                            editable=True,
                            row_deletable=True,
                            filter_action="native",
                            sort_action="native",
                            page_size=10,
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'center', 'padding': '5px', 'border': '1px solid white', 'fontSize': 14, 'backgroundColor': '#1e1e1e', 'color': 'white', 'whiteSpace': 'nowrap'},
                            style_header={'backgroundColor': '#0074D9', 'color': 'white', 'fontWeight': 'bold'}
                        )
                    ])
                ], style={'backgroundColor': '#1e1e1e', 'color': 'white'})
            ])
        ])
    ], style={'backgroundColor': '#121212', 'color': 'white', 'maxWidth': '100%'})
        

# define containers info layout
# Define the Containers Information Page
def containers_page(df_containers_info):
    # Add a "Diagram Link" column with URLs for each container
    df_containers_info["Diagram Link"] = df_containers_info["Container Name"].apply(
    lambda container_id: f"[View Details](/container/{container_id})"
)

    # Convert URLs to clickable links
    table_data = df_containers_info.to_dict('records')
    for row in table_data:
        row["Diagram Link"] = html.A("View Diagram", href=row["Diagram Link"], target="_blank", style={"color": "cyan"})

    # get containers cpu usage diagram
    cpu_usages_diag = generate_cpu_usages_fig()
    mem_usages_diag = generate_memory_usages_fig()
    return html.Div(
        [    
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Total CPU Usage", style={'color': 'white'})),
                    dbc.CardBody([
                        dcc.Graph(
                            id='cpu-usage-histogram',
                            figure=cpu_usages_diag,
                            style={'backgroundColor': 'gray'}
                        )
                    ])
                ], style={'backgroundColor': 'gray', 'color': 'white'}),
                dcc.Interval(id='interval-update-cpu-hist', interval=5000, n_intervals=0)
            ], width=6, lg=6, md=12, sm=12),  # Ensure proper sizing on all screen sizes

             dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Total Memory Usage", style={'color': 'white'})),
                    dbc.CardBody([
                        dcc.Graph(
                            id='memory-usage-histogram',
                            figure=mem_usages_diag,
                            style={'backgroundColor': 'gray'}
                        )
                    ])
                ], style={'backgroundColor': 'gray', 'color': 'white'}),
                dcc.Interval(id='interval-update-memory-hist', interval=5000, n_intervals=0)
            ], width=6, lg=6, md=12, sm=12)  # Ensure proper sizing on all screen sizes
        ], justify="center", className="g-0"),
  
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Containers Information", style={'color': 'white'})),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id='containers-info-table',
                            columns=[{"name": col, "id": col, "presentation": "markdown"} for col in df_containers_info.columns],  # Enable markdown for links
                            data=table_data,  # Pass updated data with links
                            editable=True,
                            row_deletable=True,
                            filter_action="native",
                            sort_action="native",
                            page_size=10,
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'center', 'padding': '5px', 'border': '1px solid white', 'fontSize': 14, 'backgroundColor': '#1e1e1e', 'color': 'white', 'whiteSpace': 'nowrap'},
                            style_header={'backgroundColor': '#0074D9', 'color': 'white', 'fontWeight': 'bold'}
                        ),
                        dcc.Interval(
                            id='interval-component-containers',
                            interval=10000,  # 5 seconds
                            n_intervals=0
                        ),
                        html.Label("Update Interval (seconds):"),
                        dcc.Slider(
                            id='interval-slider',
                            min=1, max=10, step=1,
                            value=5,
                            marks={i: str(i) for i in range(1, 11)}
                        )
                    ])
                ], style={'backgroundColor': '#1e1e1e', 'color': 'white'})
            ])
        ])
    ], style={'backgroundColor': '#121212', 'color': 'white', 'maxWidth': '100%'})


def applications_page(DAG_elements):
    return html.Div([
        html.H3("BGO Workflow"),
        
        html.Div([
        # Cytoscape Graph
        cyto.Cytoscape(
            id='graph',
            elements=DAG_elements,
            layout={'name': 'cose'},  # Force-directed layout
            style={'width': '700px', 'height': '800px'},
            #events={
            #    'tapNode': True,  # Ensure that tapNode event is enabled
            #    },
            stylesheet=[
                # Node style with labels inside the node
                {
                    "selector": ".microservice",
                    "style": {
                        "content": "data(label)",
                        "background-color": "#0074D9",
                        "color": "white",
                        "text-halign": "center",
                        "text-valign": "center",
                        "font-size": "14px",
                        "width": "50px",
                        "height": "50px",
                        "shape": "ellipse",
                        "text-outline-width": 2,
                        "text-outline-color": "#0056A4",
                        "border-width": 2,
                        "border-color": "white",
                        "cursor": "pointer"  # Ensure nodes are clickable
                    }
                },
                # Edge style with labels
                {
                    "selector": "edge",
                    "style": {
                        "curve-style": "bezier",
                        "target-arrow-shape": "triangle",
                        "arrow-scale": 1.5,
                        "label": "data(label)",  # Display edge labels
                        "font-size": "12px",
                        "text-rotation": "autorotate",  # Rotate label along the edge
                        "text-background-opacity": 1,
                        "text-background-color": "white",
                        "text-background-shape": "round-rectangle",
                        "text-border-color": "black",
                        "text-border-width": 1,
                        "text-border-opacity": 1
                    }
                }
            ]
        ),
        # Right: Microservice Details Panel
        html.Div(id='service-info-panel', children=html.H3("Detailed BGO"), style={
        'border': '1px solid red',
        'backgroundColor': 'lightyellow',
        'padding': '20px',
        'height': '200px',
        'width': '300px',
    })
        ])
        ])

def generate_cpu_usages_fig():
    '''
    This function reads cpu usage history for all containers and generates the figure for representing them
    together.
    '''
    if not config.cpu_usages:
            return {'data': [], 'layout': {}}

    figure = {
        'data': [],
        'layout': {
            'title': 'CPU Usage of Each Container Over Time',
            'xaxis': {'title': 'Time (seconds)'},
            'yaxis': {'title': 'CPU Usage (%)'},
            'showlegend': True
        }
    }

    colors = pc.qualitative.Plotly 
    color_map = {} 

    # Assuming `config.cpu_usages` is a dictionary where:
    # - Keys are container names
    # - Values are lists of CPU usage percentages over time
    for idx, (container_name, usage_values) in enumerate(config.cpu_usages.items()):
        color = colors[idx % len(colors)]
        color_map[container_name] = color 

        figure['data'].append({
            'x': config.times,  # Common time axis for all containers
            'y': usage_values,   # CPU usage for the current container
            'type': 'line',
            'name': container_name,  # Container name in legend
            'line': {'width': 2},
            'fill': 'tozeroy',  # Fill area under the curve to y=0
            'fillcolor': f'rgba{tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (0.3,)}',  # Transparent fill

        })
            
    return figure


def generate_memory_usages_fig():
    '''
    This function reads memory usage history for all containers and generates the figure for representing them
    together.
    '''
    if not config.mem_usages:
            return {'data': [], 'layout': {}}

    figure = {
        'data': [],
        'layout': {
            'title': 'Memory Usage of Each Container Over Time',
            'xaxis': {'title': 'Time (seconds)'},
            'yaxis': {'title': 'Memory Usage (%)'},
            'showlegend': True
        }
    }

    colors = pc.qualitative.Plotly 
    color_map = {} 

    # Assuming `config.mem_usages` is a dictionary where:
    # - Keys are container names
    # - Values are lists of Mem usage percentages over time
    for idx, (container_name, usage_values) in enumerate(config.mem_usages.items()):
        color = colors[idx % len(colors)]
        color_map[container_name] = color 

        figure['data'].append({
            'x': config.times,  # Common time axis for all containers
            'y': usage_values,   # CPU usage for the current container
            'type': 'line',
            'name': container_name,  # Container name in legend
            'line': {'width': 2},
            'fill': 'tozeroy',  # Fill area under the curve to y=0
            'fillcolor': f'rgba{tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (0.3,)}',  # Transparent fill

        })
            
    return figure

def container_details_page(containers_info_df):

    return html.Div([
        html.H3(f"Container Details: a", className="text-center"),
        html.Br(),

        '''
        dbc.Card([
            dbc.CardHeader(html.H4("Container Information", style={'color': 'white'})),
            dbc.CardBody([
                html.P(f"**Container ID:** {container_id}", style={'color': 'white'}),
                html.P(f"**Status:** {container.status}", style={'color': 'white'}),
                html.P(f"**Image:** {container.image.tags[0]}", style={'color': 'white'}),
                html.P(f"**Created At:** {container.attrs['Created']}", style={'color': 'white'}),
                html.P(f"**Command:** {container.attrs['Config']['Cmd']}", style={'color': 'white'}),
            ])
        ], style={'backgroundColor': '#1e1e1e'}),

        html.Br(),

        dbc.Card([
            dbc.CardHeader(html.H4("Resource Usage", style={'color': 'white'})),
            dbc.CardBody([
                html.P(f"**CPU Usage:** {stats['cpu_stats']['cpu_usage']['total_usage']} ns", style={'color': 'white'}),
                html.P(f"**Memory Usage:** {stats['memory_stats']['usage'] / (1024**2):.2f} MB", style={'color': 'white'}),
                html.P(f"**Network Received:** {stats['networks']['eth0']['rx_bytes'] / (1024**2):.2f} MB", style={'color': 'white'}),
                html.P(f"**Network Transmitted:** {stats['networks']['eth0']['tx_bytes'] / (1024**2):.2f} MB", style={'color': 'white'}),
            ])
        ], style={'backgroundColor': '#1e1e1e'}),

        html.Br(),
        dbc.Button("Back to Containers", href="/containers", color="primary")
    '''
    ], style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'})
