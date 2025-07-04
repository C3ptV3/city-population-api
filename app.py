#!/usr/bin/env python3
"""
City Population API
A simple REST API to manage city population data using Flask and Elasticsearch
"""

import os
import logging
from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


ES_HOST = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
ES_PORT = int(os.environ.get('ELASTICSEARCH_PORT', 9200))
ES_INDEX = 'cities'


def get_es_client():
    """Get Elasticsearch client with connection retry logic"""
    max_retries = 5
    retry_delay = 5
    
    for i in range(max_retries):
        try:
            es = Elasticsearch(
                [{'host': ES_HOST, 'port': ES_PORT, 'scheme': 'http'}],
                verify_certs=False,
                ssl_show_warn=False
            )
            if es.ping():
                logger.info(f"Successfully connected to Elasticsearch at {ES_HOST}:{ES_PORT}")
                return es
        except ConnectionError:
            logger.warning(f"Failed to connect to Elasticsearch (attempt {i+1}/{max_retries})")
            if i < max_retries - 1:
                time.sleep(retry_delay)
    
    raise ConnectionError(f"Could not connect to Elasticsearch at {ES_HOST}:{ES_PORT}")


es = None

def init_elasticsearch():
    """Initialize Elasticsearch connection and create index if needed"""
    global es
    es = get_es_client()
    
   
    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(
            index=ES_INDEX,
            body={
                "mappings": {
                    "properties": {
                        "city": {"type": "keyword"},
                        "population": {"type": "long"}
                    }
                }
            }
        )
        logger.info(f"Created index '{ES_INDEX}'")

def ensure_elasticsearch():
    """Ensure Elasticsearch is connected before processing requests"""
    global es
    if es is None or not es.ping():
        init_elasticsearch()


try:
    init_elasticsearch()
except Exception as e:
    logger.error(f"Failed to initialize Elasticsearch on startup: {e}")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        if es and es.ping():
            return jsonify({"status": "OK", "elasticsearch": "connected"}), 200
        else:
            return jsonify({"status": "ERROR", "elasticsearch": "disconnected"}), 503
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 503

@app.route('/city', methods=['POST', 'PUT'])
def upsert_city():
    """Insert or update a city and its population"""
    try:
        
        ensure_elasticsearch()
        
        data = request.get_json()
        
        
        if not data or 'city' not in data or 'population' not in data:
            return jsonify({
                "error": "Invalid input. Required fields: 'city' and 'population'"
            }), 400
        
        city = data['city'].strip()
        population = data['population']
        
        
        if not city:
            return jsonify({"error": "City name cannot be empty"}), 400
        
        
        try:
            population = int(population)
            if population < 0:
                return jsonify({"error": "Population must be non-negative"}), 400
        except (TypeError, ValueError):
            return jsonify({"error": "Population must be a valid integer"}), 400
        
        
        response = es.index(
            index=ES_INDEX,
            id=city.lower(),  
            body={
                "city": city,
                "population": population
            }
        )
        
        action = "updated" if response['result'] == 'updated' else "created"
        return jsonify({
            "message": f"City '{city}' {action} successfully",
            "city": city,
            "population": population
        }), 200
        
    except Exception as e:
        logger.error(f"Error upserting city: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/city/<city_name>', methods=['GET'])
def get_city_population(city_name):
    """Retrieve the population of a city"""
    try:
        
        ensure_elasticsearch()
        
        
        response = es.get(index=ES_INDEX, id=city_name.lower())
        
        city_data = response['_source']
        return jsonify({
            "city": city_data['city'],
            "population": city_data['population']
        }), 200
        
    except NotFoundError:
        return jsonify({"error": f"City '{city_name}' not found"}), 404
    except Exception as e:
        logger.error(f"Error retrieving city: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/cities', methods=['GET'])
def list_cities():
    """List all cities (optional endpoint for convenience)"""
    try:
        
        ensure_elasticsearch()
        
        
        response = es.search(
            index=ES_INDEX,
            body={
                "query": {"match_all": {}},
                "size": 10000  
            }
        )
        
        cities = []
        for hit in response['hits']['hits']:
            cities.append({
                "city": hit['_source']['city'],
                "population": hit['_source']['population']
            })
        
        return jsonify({
            "total": len(cities),
            "cities": cities
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing cities: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
