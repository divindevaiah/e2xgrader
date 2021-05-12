import json
import os

from tornado import web
from nbgrader.server_extensions.formgrader.base import check_xsrf

from .base import E2xBaseApiHandler as BaseApiHandler
from e2xgrader.apps.api import E2xGradebook
from multiprocessing import Process, Value


class AutogradeAll(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self):
        assignment_id = self.get_argument('assignment_id')
        p = Process(target = self.api.autograde_all, args = (assignment_id,))
        p.start()


class AutogradingProgess(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self):
        result = {'autograde_progress' : self.api.autograde_progress.value, 'autograde_flag' : self.api.autograde_flag.value}
        self.write(json.dumps(result))


class UpdateNotebook(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self):
        assignment_id = self.get_argument('assignment_id')
        notebook_id = self.get_argument('notebook_id')
        cells = self.get_argument('cells')
        cells = eval(cells.split()[0])
        db_url = 'sqlite:///' + os.path.join(os.getcwd(), 'gradebook.db')
        gb = E2xGradebook(db_url)
        checksum_id = []
        for cell in cells:
            checksum_single = gb.update_cell_content(cell, notebook_id, assignment_id)
            checksum_id.append(checksum_single)
            gb.update_or_create_source_cell(name = cell, notebook = notebook_id, assignment = assignment_id, checksum = checksum_single)
        self.write(json.dumps(checksum_id))


class FindUpdatedCells(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self):
        assignment_id = self.get_argument('assignment_id')
        notebook_id = self.get_argument('notebook_id')
        db_url = 'sqlite:///' + os.path.join(os.getcwd(), 'gradebook.db')
        gb = E2xGradebook(db_url)
        updated_cells = gb.list_updated_cells(notebook_id, assignment_id)
        self.write(json.dumps(updated_cells))


class GetNotebook(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self):
        assignment_id = self.get_argument('assignment_id')
        db_url = 'sqlite:///' + os.path.join(os.getcwd(), 'gradebook.db')
        gb = E2xGradebook(db_url)
        assignment_object = gb.find_assignment(assignment_id)
        notebooks = []
        for assignment in assignment_object.notebooks:
            notebooks.append(assignment.name)
        self.write(json.dumps(notebooks))


class SolutionCellCollectionHandler(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self, assignment_id, notebook_id):
        cells = self.api.get_solution_cell_ids(assignment_id, notebook_id)
        self.write(json.dumps(cells))


class SubmittedTaskCollectionHandler(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self, assignment_id, notebook_id, task_id):
        submissions = self.api.get_task_submissions(assignment_id, notebook_id, task_id)
        self.write(json.dumps(submissions))


default_handlers = [
    (r"/formgrader/api/solution_cells/([^/]+)/([^/]+)", SolutionCellCollectionHandler),
    (r"/formgrader/api/submitted_tasks/([^/]+)/([^/]+)/([^/]+)", SubmittedTaskCollectionHandler),
    (r'/formgrader/api/get_notebook/?', GetNotebook),
    (r'/formgrader/api/find_updated_cell/?', FindUpdatedCells),
    (r'/formgrader/api/update_notebook/?', UpdateNotebook),
    (r'/formgrader/api/autograde_all/?', AutogradeAll),
    (r'/formgrader/api/autograding_progress/?', AutogradingProgess),
]
