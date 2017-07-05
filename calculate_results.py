#!/usr/bin/env python
import os


if __name__ == '__main__':
    test_names = set()
    server_names = set()
    results = {}

    for result in os.listdir('gatling/target/gatling'):
        if os.path.isdir(os.path.join('gatling/target/gatling', result)):
            test_name, server_name, _ = result.split('-')
            test_names.add(test_name)
            server_names.add(server_name)
            results[(test_name, server_name)] = result

    test_names = sorted(test_names)
    server_names = sorted(server_names)
    with open('result.html', 'w') as output:
        output.write('''
                     <html>
                        <head>
                            <title>Results</title>
                        </head>
                        <body>
                            <h1>Result<h1>
                            <table>
                                <thead>
                                    <th>Server</th>
                    ''')
        for test_name in test_names:
            output.write('<th>' + test_name + '</th>')
        output.write('</thead><tbody>')
        for server_name in server_names:
            output.write('<tr><td>' + server_name + '</td>')
            for test_name in test_names:
                result = results.get((test_name, server_name))
                if result is None:
                    output.write('<td>N/A</td>')
                    continue
                with open(os.path.join('gatling/target/gatling', result, 'simulation.log')) as simulation_log:
                    requests = []
                    for row in simulation_log:
                        row = row.split('\t')
                        if row[0] == 'RUN':
                            start_time = float(row[4]) / 1000.0
                        if row[0] == 'REQUEST':
                            requests.append((
                                float(row[5]) / 1000.0,  # time
                                row[7]  # status
                            ))
                    for i, (time, status) in enumerate(sorted(requests)):
                        if status == 'KO':
                            rps = 2 * i / (time - start_time)
                            break
                    else:
                        rps = 2 * len(requests) / 60.0
                    output.write('<td>%f</td>' % rps)
            output.write('</tr>')
        output.write('</table></body></html>')
