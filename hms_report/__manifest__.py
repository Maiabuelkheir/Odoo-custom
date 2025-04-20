{
    'name': 'HMS Report',
    'version': '1.0',
    'category': 'Healthcare',
    'description': 'Generate patient status reports.',
    'author': 'Mai',
    'depends': ['base', 'hms'],
    'data': [
    'reports/patient_status_report.xml',  
],

    'qweb': ['reports/patient_status_report.xml'],

    'installable': True,
    'application': False,
}
