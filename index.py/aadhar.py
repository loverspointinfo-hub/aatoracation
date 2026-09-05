from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# ==================== কনফিগারেশন ====================
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36 Edg/145.0.0.0',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/json',
    'deptid': '317',
    'srvid': '1519',
    'subsid': '0',
    'subsid2': '0',
    'formtrkr': '0',
    'x-api-key': 'VKE9PnbY5k1ZYapR5PyYQ33I26sXTX569Ed7eqyg',
    'origin': 'https://web.umang.gov.in',
    'referer': 'https://web.umang.gov.in/',
    'tenantid': '',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site'
}

# বেস পেলোড
BASE_PAYLOAD = {
    "tkn": "yy054622e1-d289-403b-883a-b4c20235b9ef/2",
    "trkr": "213132",
    "lang": "en",
    "lat": "21",
    "lon": "90",
    "lac": "90",
    "usag": "90",
    "apitrkr": "123234",
    "usrid": "09",
    "mode": "web",
    "pltfrm": "windows",
    "did": "123234",
    "deptid": "317",
    "formtrkr": "0",
    "srvid": "1519",
    "subsid": "0",
    "subsid2": "0",
    "sessionId": "801005114414399",
    "userName": "umang",
    "token": "Um@93259@"
}

# ==================== রেশন কার্ড ফাংশন ====================
def get_ration_by_family_id(family_id):
    """Family ID দিয়ে রেশন কার্ডের বিস্তারিত তথ্য আনে"""
    
    url = "https://apigw.umangapp.in/onorcApi/ws1/getrationcard"
    
    payload = BASE_PAYLOAD.copy()
    payload["id"] = str(family_id)
    payload["idType"] = "R"
    
    try:
        print(f"\n📤 Fetching Ration Card for Family ID: {family_id}")
        response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "raw": response.text[:500]
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== Aadhaar সার্চ ফাংশন (আপডেট করবে) ====================
def get_family_by_aadhaar(aadhaar):
    """Aadhaar নাম্বার দিয়ে Family ID বের করে"""
    
    # TODO: Aadhaar API URL টা এখানে বসাও
    url = "https://apigw.umangapp.in/onorcApi/ws1/searchbyuid"  # এইটা কাজ করছে না
    
    payload = BASE_PAYLOAD.copy()
    payload["uid"] = str(aadhaar)
    payload["idType"] = "UID"
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                family_id = data['data'][0].get('familyid')
                return {"success": True, "family_id": family_id, "raw": data}
        return {"success": False, "error": "Family ID not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== API Endpoints ====================

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "Umang Ration Card API",
        "version": "2.0.0",
        "author": "AKASHHACKER",
        "endpoints": [
            {"path": "/ration/<family_id>", "method": "GET", "description": "Ration Card Number দিয়ে ডিটেলস"},
            {"path": "/aadhaar/<aadhaar>", "method": "GET", "description": "Aadhaar নাম্বার দিয়ে Family ID খোঁজা"},
            {"path": "/aadhaar-to-ration/<aadhaar>", "method": "GET", "description": "Aadhaar → Family ID → Ration Card"}
        ]
    })

@app.route('/ration/<family_id>', methods=['GET'])
def get_ration(family_id):
    """Ration Card Number দিয়ে সরাসরি ডিটেলস"""
    result = get_ration_by_family_id(family_id)
    if result['success']:
        return jsonify({"success": True, "family_id": family_id, "data": result['data']})
    return jsonify(result), 400

@app.route('/aadhaar/<aadhaar>', methods=['GET'])
def search_aadhaar(aadhaar):
    """শুধু Aadhaar দিয়ে Family ID খোঁজা"""
    if not aadhaar.isdigit() or len(aadhaar) != 12:
        return jsonify({"success": False, "error": "Invalid Aadhaar"}), 400
    
    result = get_family_by_aadhaar(aadhaar)
    if result['success']:
        return jsonify(result)
    return jsonify(result), 404

@app.route('/aadhaar-to-ration/<aadhaar>', methods=['GET'])
def aadhaar_to_ration(aadhaar):
    """Aadhaar → Family ID → Ration Card"""
    if not aadhaar.isdigit() or len(aadhaar) != 12:
        return jsonify({"success": False, "error": "Invalid Aadhaar"}), 400
    
    # Step 1: Aadhaar দিয়ে Family ID খোঁজো
    family_result = get_family_by_aadhaar(aadhaar)
    if not family_result['success']:
        return jsonify({"success": False, "step": "aadhaar_search", "error": family_result['error']}), 404
    
    family_id = family_result['family_id']
    
    # Step 2: Family ID দিয়ে রেশন কার্ড আনো
    ration_result = get_ration_by_family_id(family_id)
    if not ration_result['success']:
        return jsonify({
            "success": False,
            "step": "ration_details",
            "family_id": family_id,
            "error": ration_result['error']
        }), 500
    
    return jsonify({
        "success": True,
        "aadhaar": aadhaar,
        "family_id": family_id,
        "data": ration_result['data']
    })

# ==================== লোকাল রান ====================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 UMANG RATION CARD API v2.0")
    print("📍 Aadhaar + Ration Card Combined")
    print("=" * 60)
    print("\n📌 Available Endpoints:")
    print("  • GET /ration/1906455974")
    print("  • GET /aadhaar/393933081942")
    print("  • GET /aadhaar-to-ration/393933081942")
    print("\n" + "=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)