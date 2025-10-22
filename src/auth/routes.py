"""Authentication blueprint and endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    unset_jwt_cookies,
)

from pymongo.collection import Collection
from src.auth.passwords import hash_password, verify_password
from src.auth.validators import validate_registration_input


def create_auth_blueprint(users_collection: Collection) -> Blueprint:
    """Create the authentication blueprint and register routes."""

    auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

    @auth_bp.post("/register")
    def register() -> Any:
        payload = request.get_json() or {}
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""

        is_valid, error_message = validate_registration_input(email, password)
        if not is_valid:
            return jsonify({"success": False, "error": error_message}), 400

        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return jsonify({"success": False, "error": "Email already registered."}), 409

        password_hash = hash_password(password)
        now = datetime.utcnow()

        insert_result = users_collection.insert_one({
            "email": email,
            "password_hash": password_hash,
            "created_at": now,
            "updated_at": now,
        })

        user_id = str(insert_result.inserted_id)
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        response = jsonify({
            "success": True,
            "user": {
                "id": user_id,
                "email": email,
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
        })
        return response, 201

    @auth_bp.post("/login")
    def login() -> Any:
        payload = request.get_json() or {}
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""

        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required."}), 400

        user = users_collection.find_one({"email": email})
        if not user or not verify_password(user["password_hash"], password):
            return jsonify({"success": False, "error": "Invalid credentials."}), 401

        user_id = str(user["_id"])
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        response = jsonify({
            "success": True,
            "user": {
                "id": user_id,
                "email": email,
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
        })
        return response

    @auth_bp.post("/refresh")
    @jwt_required(refresh=True)
    def refresh() -> Any:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify({"success": True, "access_token": access_token})

    @auth_bp.post("/logout")
    def logout() -> Any:
        response = jsonify({"success": True})
        unset_jwt_cookies(response)
        return response

    return auth_bp
