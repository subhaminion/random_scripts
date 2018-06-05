import csv
from ak_vendor.enums import PlatformEnum, RiskEnum
from mycroft.core.models import Vulnerability
from mycroft.core.dbapi import get_files, \
    get_ordered_analyses_for_file


def generate_data():
    RISK_OBJ = {
        RiskEnum.CRITICAL: 'Critical',
        RiskEnum.HIGH: 'High',
        RiskEnum.MEDIUM: 'Medium',
        RiskEnum.LOW: 'Low',
        RiskEnum.PASSED: 'Passed',
        RiskEnum.UNKNOWN: 'Unknown'
    }

    PLATFORM_OBJ = {
        PlatformEnum.ANDROID: 'ANDROID',
        PlatformEnum.IOS: 'IOS',
        PlatformEnum.WINDOWS: 'WINDOWS',
        PlatformEnum.COMMON: 'COMMON',
    }

    vulns = [
        str(vul)
        for vul in Vulnerability.objects.all().order_by('id')
    ]

    files = get_files().prefetch_related('analyses').select_related(
        'project', 'project__owner'
    )

    with open('all_scans.csv', 'w') as csvfile:
        filewriter = csv.writer(
            csvfile, delimiter=',')
        filewriter.writerow([
            'project_id', 'user_id',
            'file_id', 'package_name',
            'platform', *vulns
        ])

        for file in files:
            data_initial = [
                file.project.id, file.project.owner.username,
                file.id, file.project.package_name,
                PLATFORM_OBJ.get(file.project.platform)
            ]
            analysis_objs = get_ordered_analyses_for_file(file)
            analysis_data = [
                RISK_OBJ[
                    analysis_obj['analysis'].risk
                    if analysis_obj['analysis'] else RiskEnum.UNKNOWN
                ]
                for analysis_obj in analysis_objs
            ]
            filewriter.writerow(data_initial + analysis_data)
