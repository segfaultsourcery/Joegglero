# Joegglero
This is pretty much like slapping half of a REST API on os.system(). What could go wrong?

Tested on Python 3.6.


## Submit a simple job

### Submit a job

    Linux:
    http://localhost:5000/submit/echo%20test

    Windows:
    http://localhost:5000/submit/powershell%20/c%20echo%20test
    
### Check job status

    All jobs:
    http://localhost:5000/status
    
    Single job:
    http://localhost:5000/status/1 
    
### Get job result

    http://localhost:5000/result/1
    
## Submit a more complex job

A more robust way of submitting a job is by posting an array of terms.

    import requests
    
    url = "http://localhost:5000/submit"
    result = requests.post(url, json=['echo', 'this is a more robust test'])

## Submit a number of jobs to be executed simultaneously

    import requests
    
    url = "http://localhost:5000/submit_many"
    result = requests.post(url, json=[
        ['echo', 'It's impossible to say which one of these will finish first.'],
        ['echo', 'It's impossible to say which one of these will finish first.']
    ])

## Submit a number of jobs to be executed in a queue

    import requests
    
    url = "http://localhost:5000/submit_chain"
    result = requests.post(url, json=[
        ['echo', 'This will execute first.'],
        ['echo', 'This will execute second.']
    ])
