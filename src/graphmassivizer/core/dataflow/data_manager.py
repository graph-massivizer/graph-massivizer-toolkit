
import os
from datetime import datetime, UTC


class DataManager:
    def __init__(self, base_dir: str, fs):
        self.base_dir = base_dir
        self.fs = fs
        self.fs.create(base_dir)
        self.graphs_metadata = {}  # format: {workflow_id/job_id: [list of versions]}
        self.logger = self.fs.get_logger("DataManager")

    def _get_timestamp(self):
        return datetime.now(UTC).strftime("%Y%m%d%H%M%S")

    def generate_graph_id(self, workflow_id: str, job_id: str, timestamp: str = None):
        if not timestamp:
            timestamp = self._get_timestamp()
        return f"{workflow_id}/{job_id}/{timestamp}"

    def generate_graph_path(self, workflow_id: str, job_id: str, timestamp: str = None):
        """
        Generate a path to store graph data uniquely for each job execution.
        """
        if not timestamp:
            timestamp = self._get_timestamp()

        graph_id = self.generate_graph_id(workflow_id, job_id, timestamp)
        graph_folder_path = os.path.join(self.base_dir, graph_id)
        graph_path = os.path.join(graph_folder_path, "object.pkl")

        metadata_entry = {
            'workflow_id': workflow_id,
			'job_id': job_id,
            'graph_id': graph_id,
            'path': graph_path,
            'nodes': 0,
            'edges': 0,
            'generated_bgo': '',
            'gen_bgo_input_graph_ids': [],
            'creation_timestamp': timestamp,
            'status': 'initialized'
        }

        if f"{workflow_id}/{job_id}" not in self.graphs_metadata:
            self.graphs_metadata[f"{workflow_id}/{job_id}"] = []
        self.graphs_metadata[f"{workflow_id}/{job_id}"].append(metadata_entry)

        self.logger.info(f"Generated path for graph: {graph_path}")
        return graph_path, timestamp

    def update_graph_metadata(self, workflow_id: str, job_id: str, timestamp: str,
                              nodes: int, edges: int, generated_bgo: str,
                              gen_bgo_input_graph_ids: list, status='complete'):
        """
        Update the metadata for a graph with a specific timestamp version.
        """
        versions = self.graphs_metadata.get(f"{workflow_id}/{job_id}", [])
        for entry in versions:
            if entry['creation_timestamp'] == timestamp:
                entry.update({
                    'nodes': nodes,
                    'edges': edges,
                    'generated_bgo': generated_bgo,
                    'gen_bgo_input_graph_ids': gen_bgo_input_graph_ids,
                    'status': status
                })
                self.logger.info(f"Updated metadata for {workflow_id}/{job_id}/{timestamp}")
                return

        self.logger.warning(f"No graph entry found for update: {workflow_id}/{job_id}/{timestamp}")

    def retrieve_latest_path(self, workflow_id: str, job_id: str):
        """
        Retrieve the most recent version of the graph path for a given job.
        """
        versions = self.graphs_metadata.get(f"{workflow_id}/{job_id}", [])
        if not versions:
            self.logger.warning(f"No graphs found for: {workflow_id}/{job_id}")
            return None
        latest = sorted(versions, key=lambda x: x['creation_timestamp'], reverse=True)[0]
        return latest['path']

    def retrieve_all_versions(self, workflow_id: str, job_id: str):
        """
        Retrieve all available versions for a given job.
        """
        return self.graphs_metadata.get(f"{workflow_id}/{job_id}", [])

    def lookup(self, workflow_id: str, job_id: str, timestamp: str = None):
        """
        Lookup the graph path for a given workflow/job/timestamp.
        If timestamp is None, return the latest version.
        """
        versions = self.graphs_metadata.get(f"{workflow_id}/{job_id}", [])
        if not versions:
            self.logger.warning(f"No metadata found for: {workflow_id}/{job_id}")
            return None

        if timestamp:
            for entry in versions:
                if entry['creation_timestamp'] == timestamp:
                    return entry['path']
            self.logger.warning(f"No entry found for timestamp: {timestamp}")
            return None
        else:
            return self.retrieve_latest_path(workflow_id, job_id)
