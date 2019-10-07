class ProcessStatus:
    RUNNING = 'RUNNING'
    ERROR = 'ERROR'
    SUCCESS = 'SUCCESS'

    def __init__(self, process_id, start_dtm, end_dtm=None, status=RUNNING, cnt=0):
        self.process_id = process_id
        self.start_dtm = start_dtm
        self.end_dtm = end_dtm
        self.status = status
        self.cnt = cnt

    def copy(self):
        return ProcessStatus(process_id=self.process_id,
                             start_dtm=self.start_dtm,
                             end_dtm=self.end_dtm,
                             status=self.status,
                             cnt=self.cnt)

    def is_success(self):
        return self.status == ProcessStatus.SUCCESS

    def is_running(self):
        return self.status == ProcessStatus.RUNNING

    def is_error(self):
        return self.status == ProcessStatus.ERROR

    def set_succeeded(self):
        self.status = ProcessStatus.SUCCESS

    def set_error(self):
        self.status = ProcessStatus.ERROR

    def set_running(self):
        self.status = ProcessStatus.RUNNING

    def get_as_json(self):
        return {'process_id': self.process_id,
                'start_dtm': self.start_dtm,
                'end_dtm': self.end_dtm,
                'status': self.status,
                'cnt': self.cnt}
