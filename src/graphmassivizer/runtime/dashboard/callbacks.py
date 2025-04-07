from dash import Input, Output, State, html
import config
import dash
import pandas as pd
from layout import zookeeper_page, containers_page, applications_page, generate_cpu_usages_fig, generate_memory_usages_fig, container_details_page


def register_callbacks(app, containers_info_df, df_znodes_data, znodes_hierarchy_graph_elements, DAG_elements):
    @app.callback(
    Output('containers-info-table', 'data'),
    Input('interval-component-containers', 'n_intervals')
)
    def update_table(n_intervals):
        print(f"Triggered update {n_intervals}")
        df = config.dashboard_obj.list_all_containers_info_in_network_multithread()
        if df is None or df.empty:
            print("Warning: No data received for containers!")
            return []
        
        print(f'df inside update_table columns are: {df.columns} and its len is {df.shape[0]} dataframe is : {df.to_string()}')
        return list(df.to_dict('records'))

    # tocheck 
    @app.callback(
        dash.dependencies.Output('cpu-usage-histogram', 'figure'),
        [dash.dependencies.Input('interval-update-cpu-hist', 'n_intervals')]
    )
    def update_graph_cpu_hist(n_intervals):
        print(f'Update CPU usage graph triggered with interval num {n_intervals}')
        print(f'CPU usages are {config.cpu_usages}')

        figure = generate_cpu_usages_fig()

        return figure


    @app.callback(
        dash.dependencies.Output('memory-usage-histogram', 'figure'),
        [dash.dependencies.Input('interval-update-memory-hist', 'n_intervals')]
    )
    def update_graph_memory_hist(n_intervals):
        # Create a histogram plot using the updated data
        print(f'Update memory usage histogram graph triggered with interval num {n_intervals}')
        print(f'mem_usages are {config.mem_usages}')
        figure = generate_memory_usages_fig()
        
        return figure
        
        
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname"),
    )
    def display_page(pathname):
        print(f"DEBUG: df_containers_info = {containers_info_df}")
        print(f"DEBUG: df_znodes_data = {df_znodes_data}")
        print(f"DEBUG: znodes_hierarchy_graph_elements = {znodes_hierarchy_graph_elements}")
        try:
            print(f"DEBUG: Current pathname = {pathname}")  # Debugging output
            
            if pathname == "/containers":
                return containers_page(containers_info_df)  # Ensure df_containers_info is defined
            elif pathname == "/" or pathname == "/zookeeper":
                return zookeeper_page(df_znodes_data, znodes_hierarchy_graph_elements)
            elif pathname == "/applications":
                return applications_page(DAG_elements)
            elif pathname.startswith("/container/"):  # Dynamic route
                #container_id = pathname.split("/")[-1]
                return container_details_page(containers_info_df)
            else:
                return html.H3("404: Page Not Found", style={"color": "white", "textAlign": "center"})
        
        except Exception as e:
            print(f"ERROR in display_page: {e}")  # Print error to the console
            return html.H3("An error occurred", style={"color": "red", "textAlign": "center"})

    

    # Callback to update service details when a node is clicked
    @app.callback(
        Output('service-info-panel', 'children'),
        Input('graph', 'tapNodeData')  # Triggered when a node is clicked
    )
    def display_service_info(node_data):
        print(f"DEBUG: tapNodeData received: {node_data}")
        if not node_data:
            return "Click a service node to see details."
        
        # temp
        return html.Div([
        html.H4("Service: Test Service"),
        html.P("URL: http://example.com"),
        html.P("Implementations: Service A")
    ])
    '''
        return html.Div([
        html.H4(f"Service: {node_data.get('label', 'Unknown')}"),
        html.P(f"URL: {node_data.get('url', '#')}"),
        html.P(f"Implementations: {node_data.get('implementations', 'Unknown')}")
    ])
    '''