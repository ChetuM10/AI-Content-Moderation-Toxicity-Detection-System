"""Blueprint for analysis history and favorites endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from pymongo.errors import PyMongoError
from pymongo.collection import Collection
import logging

logger = logging.getLogger(__name__)


def create_history_blueprint(history_collection: Collection) -> Blueprint:
    """Create the history blueprint."""

    history_bp = Blueprint("history", __name__, url_prefix="/api/history")

    def _parse_object_id(value: str) -> ObjectId:
        try:
            return ObjectId(value)
        except Exception as exc:
            raise ValueError("Invalid record identifier.") from exc

    def _get_user_id_optional() -> Optional[ObjectId]:
        """Get user ID if authenticated, None otherwise."""
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                return ObjectId(identity)
        except Exception as e:
            logger.info(f"JWT verification failed: {e}")
        return None

    def _serialize_document(document: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize MongoDB document to JSON-safe format."""
        # Create a copy to avoid modifying original
        result = dict(document)

        # Convert _id to string and add as both _id and id
        result["_id"] = str(result.get("_id", ""))
        result["id"] = result["_id"]

        # Convert user_id to string if exists
        if "user_id" in result:
            result["user_id"] = str(result["user_id"])

        # Ensure created_at exists (use timestamp if not present)
        if "timestamp" in result and "created_at" not in result:
            result["created_at"] = result["timestamp"]

        # Ensure favorite field exists
        if "favorite" not in result:
            result["is_favorite"] = False
        else:
            result["is_favorite"] = result["favorite"]

        return result

    @history_bp.get("/")
    def list_history() -> Any:
        """Return the authenticated user's analysis history."""
        # Get user ID
        user_id = _get_user_id_optional()
        if not user_id:
            return jsonify({
                "success": False,
                "error": "Authentication required. Please login to view history."
            }), 401

        # Get query parameters
        limit = max(1, min(200, int(request.args.get("limit", 50))))
        query_params: Dict[str, Any] = {"user_id": user_id}

        # Handle filter parameter (toxic/safe/favorites/all)
        filter_type = request.args.get("filter", "all").lower()

        if filter_type == "toxic":
            query_params["is_toxic"] = True
        elif filter_type == "safe":
            query_params["is_toxic"] = False
        elif filter_type == "favorites":
            query_params["favorite"] = True
        # "all" doesn't add any filter

        history_items: List[Dict[str, Any]] = []

        try:
            # Sort by timestamp (or created_at) descending
            cursor = history_collection.find(
                query_params).sort("timestamp", -1).limit(limit)

            for document in cursor:
                history_items.append(_serialize_document(document))

            logger.info(
                f"Retrieved {len(history_items)} history items for user {user_id} with filter '{filter_type}'")

        except PyMongoError as db_error:
            logger.error(f"Database error: {db_error}")
            return jsonify({
                "success": False,
                "error": f"Database query failed: {db_error}"
            }), 500

        return jsonify({
            "success": True,
            "history": history_items,
            "count": len(history_items)
        })

    @history_bp.get("/<record_id>")
    def get_record(record_id: str) -> Any:
        """Return a specific analysis record by ID."""
        user_id = _get_user_id_optional()
        if not user_id:
            return jsonify({
                "success": False,
                "error": "Authentication required."
            }), 401

        try:
            parsed_id = _parse_object_id(record_id)
        except ValueError as error:
            return jsonify({"success": False, "error": str(error)}), 400

        try:
            document = history_collection.find_one({
                "_id": parsed_id,
                "user_id": user_id
            })
        except PyMongoError as db_error:
            logger.error(f"Database error: {db_error}")
            return jsonify({
                "success": False,
                "error": f"Database query failed: {db_error}"
            }), 500

        if document is None:
            return jsonify({
                "success": False,
                "error": "Record not found."
            }), 404

        # Return the COMPLETE record (serialize it properly)
        serialized = _serialize_document(document)
        logger.info(f"Retrieved record {record_id} for user {user_id}")

        # Return just the serialized document (not wrapped in {"record": ...})
        return jsonify(serialized)

    @history_bp.post("/<record_id>/favorite")
    def toggle_favorite(record_id: str) -> Any:
        """Toggle the favorite flag on a history record."""
        user_id = _get_user_id_optional()
        if not user_id:
            return jsonify({
                "success": False,
                "error": "Authentication required."
            }), 401

        try:
            parsed_id = _parse_object_id(record_id)
        except ValueError as error:
            return jsonify({"success": False, "error": str(error)}), 400

        # Get current favorite status
        try:
            current_record = history_collection.find_one({
                "_id": parsed_id,
                "user_id": user_id
            })

            if not current_record:
                return jsonify({
                    "success": False,
                    "error": "Record not found."
                }), 404

            # Toggle the favorite status
            current_favorite = current_record.get("favorite", False)
            new_favorite = not current_favorite

            # Update the record
            update_result = history_collection.update_one(
                {"_id": parsed_id, "user_id": user_id},
                {"$set": {"favorite": new_favorite}}
            )

            logger.info(
                f"Toggled favorite for record {record_id} to {new_favorite}")

            return jsonify({
                "success": True,
                "favorite": new_favorite,
                "is_favorite": new_favorite
            })

        except PyMongoError as db_error:
            logger.error(f"Database error: {db_error}")
            return jsonify({
                "success": False,
                "error": f"Database update failed: {db_error}"
            }), 500

    @history_bp.delete("/<record_id>")
    def delete_record(record_id: str) -> Any:
        """Delete a specific analysis record."""
        user_id = _get_user_id_optional()
        if not user_id:
            return jsonify({
                "success": False,
                "error": "Authentication required."
            }), 401

        try:
            parsed_id = _parse_object_id(record_id)
        except ValueError as error:
            return jsonify({"success": False, "error": str(error)}), 400

        try:
            delete_result = history_collection.delete_one({
                "_id": parsed_id,
                "user_id": user_id
            })
        except PyMongoError as db_error:
            logger.error(f"Database error: {db_error}")
            return jsonify({
                "success": False,
                "error": f"Database delete failed: {db_error}"
            }), 500

        if delete_result.deleted_count == 0:
            return jsonify({
                "success": False,
                "error": "Record not found."
            }), 404

        logger.info(f"Deleted record {record_id}")

        return jsonify({
            "success": True,
            "message": "Record deleted successfully"
        })

    return history_bp
