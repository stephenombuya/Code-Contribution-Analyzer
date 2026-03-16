"""
Report download routes — CSV, JSON, PDF.
"""
from __future__ import annotations

import logging
from io import BytesIO

from flask import Blueprint, Response, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.web.app import Analysis
from src.visualization.report_generator import ReportGenerator

logger = logging.getLogger(__name__)
reports_bp = Blueprint("reports", __name__)


@reports_bp.get("/<int:analysis_id>/<fmt>")
@jwt_required()
def download_report(analysis_id: int, fmt: str):
    """
    Download analysis report in json | csv | pdf format.
    """
    user_id = int(get_jwt_identity())

    if fmt not in ("json", "csv", "pdf"):
        return jsonify({"error": "Format must be one of: json, csv, pdf"}), 400

    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    if not analysis:
        return jsonify({"error": "Analysis not found."}), 404
    if analysis.status != "completed" or not analysis.result:
        return jsonify({"error": "Analysis not yet completed."}), 409

    gen = ReportGenerator(
        result=analysis.result,
        username=analysis.username,
        platform=analysis.platform,
    )

    filename = f"contribution_report_{analysis.username}_{analysis.platform}"

    if fmt == "json":
        data = gen.to_json()
        return Response(
            data,
            mimetype="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}.json"',
                "Content-Length": str(len(data)),
            },
        )
    elif fmt == "csv":
        data = gen.to_csv()
        return Response(
            data,
            mimetype="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}.csv"',
                "Content-Length": str(len(data)),
            },
        )
    elif fmt == "pdf":
        data = gen.to_pdf()
        return send_file(
            BytesIO(data),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{filename}.pdf",
        )
