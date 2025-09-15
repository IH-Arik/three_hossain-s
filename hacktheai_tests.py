import requests
import json

BASE = 'http://127.0.0.1:8000'

def call(m, path, data=None, expect=200):
    url = f"{BASE}{path}"
    if m == 'GET':
        r = requests.get(url)
    elif m == 'POST':
        r = requests.post(url, json=data)
    elif m == 'PUT':
        r = requests.put(url, json=data)
    elif m == 'DELETE':
        r = requests.delete(url)
    else:
        raise ValueError('method')
    print(m, path, r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
    acceptable = (expect,) if isinstance(expect, int) else tuple(expect)
    assert r.status_code in acceptable, (path, r.status_code)
    return r.json() if r.headers.get('Content-Type','').startswith('application/json') else r.text


def run():
    # Ensure clean state for voter 10
    call('DELETE', '/api/voters/10', expect=(200, 404))
    # Q1
    call('POST', '/api/voters', {'voter_id': 10, 'name': 'Test User', 'age': 25}, expect=(201, 409))
    # Q2
    call('GET', '/api/voters/10')
    # Q3
    call('GET', '/api/voters')
    # Q4
    call('PUT', '/api/voters/10', {'name': 'Test User Updated', 'age': 26})
    # Q5
    call('POST', '/api/candidates', {'candidate_id': 11, 'name': 'X', 'party': 'Blue'}, expect=(200, 409))
    # Q6 covered above
    # Q7
    call('GET', '/api/candidates')
    # Q8
    call('POST', '/api/votes', {'voter_id': 10, 'candidate_id': 11})
    # Q9
    call('GET', '/api/candidates/11/votes')
    # Q10
    call('GET', '/api/candidates?party=Blue')
    # Q11
    call('GET', '/api/results')
    # Q12
    call('GET', '/api/results/winner')
    # Q13
    call('GET', '/api/votes/timeline?candidate_id=11')
    # Q14
    call('POST', '/api/votes/weighted', {'voter_id': 10, 'candidate_id': 11})
    # Q15 – pick a broad time window
    call('GET', '/api/votes/range?candidate_id=11&from=2000-01-01T00:00:00Z&to=2100-01-01T00:00:00Z')
    # Q16
    call('POST', '/api/ballots/encrypted', {
        'election_id': 'nat-2025',
        'ciphertext': 'base64(...)',
        'zk_proof': 'base64(...)',
        'voter_pubkey': 'hex(...)',
        'nullifier': '0xabc123',
        'signature': 'base64(...)'
    }, expect=(200, 409))
    # Q17
    call('POST', '/api/results/homomorphic', {
        'election_id': 'nat-2025',
        'trustee_decrypt_shares': [
            {'trustee_id': 'T1', 'share': 's', 'proof': 'p'}
        ]
    })
    # Q18
    call('POST', '/api/analytics/dp', {
        'election_id': 'nat-2025',
        'query': { 'type': 'histogram', 'dimension': 'voter_age_bucket', 'buckets': [], 'filter': {'has_voted': True}},
        'epsilon': 0.5,
        'delta': 1e-6
    })
    # Q19
    call('POST', '/api/ballots/ranked', { 'ballots': [[11, 2, 1]] })
    # Q20
    call('POST', '/api/audits/rla', { 'election_id': 'nat-2025', 'risk_limit': 0.05 })


if __name__ == '__main__':
    run()


