from flask import Flask, jsonify, request
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import Tender, TenderStatus, Bid, BidStatus, OrganizationResponsible

app = Flask(__name__)

# Проверка доступности сервера
@app.route('/api/ping', methods=['GET'])
def ping():
    return "ok", 200

# Создание тендера
@app.route('/api/tenders/new', methods=['POST'])
def create_tender():
    data = request.json
    db: Session = SessionLocal()

    # Проверка, является ли пользователь ответственным за организацию
    responsible_user = db.query(OrganizationResponsible).filter_by(
        organization_id=data['organizationId'], user_id=data['creatorUserId']).first()

    if not responsible_user:
        return jsonify({"error": "User is not authorized to create tenders for this organization"}), 403

    new_tender = Tender(
        name=data['name'],
        description=data.get('description'),
        service_type=data['serviceType'],
        organization_id=data['organizationId']
    )
    db.add(new_tender)
    db.commit()
    return jsonify({
        "id": new_tender.id,
        "name": new_tender.name,
        "description": new_tender.description,
        "version": new_tender.version
    }), 200

# Публикация тендера
@app.route('/api/tenders/<int:tender_id>/publish', methods=['POST'])
def publish_tender(tender_id):
    db: Session = SessionLocal()
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if tender and tender.status == TenderStatus.CREATED:
        tender.status = TenderStatus.PUBLISHED
        db.commit()
        return jsonify({"message": "Tender published"}), 200
    return jsonify({"error": "Tender not found or already published"}), 404

# Закрытие тендера
@app.route('/api/tenders/<int:tender_id>/close', methods=['POST'])
def close_tender(tender_id):
    db: Session = SessionLocal()
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if tender and tender.status == TenderStatus.PUBLISHED:
        tender.status = TenderStatus.CLOSED
        db.commit()
        return jsonify({"message": "Tender closed"}), 200
    return jsonify({"error": "Tender not found or already closed"}), 404

# Получение тендеров организации
@app.route('/api/tenders/my', methods=['GET'])
def get_user_tenders():
    organization_id = request.args.get('organization_id')
    db: Session = SessionLocal()
    tenders = db.query(Tender).filter(Tender.organization_id == organization_id).all()
    return jsonify([{
        "id": tender.id,
        "name": tender.name,
        "description": tender.description
    } for tender in tenders]), 200

# Редактирование тендера
@app.route('/api/tenders/<int:tender_id>/edit', methods=['PATCH'])
def edit_tender(tender_id):
    data = request.json
    db: Session = SessionLocal()
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if tender:
        tender.name = data.get('name', tender.name)
        tender.description = data.get('description', tender.description)
        tender.version += 1
        db.commit()
        return jsonify({
            "id": tender.id,
            "name": tender.name,
            "description": tender.description,
            "version": tender.version
        }), 200
    return jsonify({"error": "Tender not found"}), 404

# Откат версии тендера
@app.route('/api/tenders/<int:tender_id>/rollback/<int:version>', methods=['PUT'])
def rollback_tender(tender_id, version):
    db: Session = SessionLocal()
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if tender and tender.version > version:
        # Логика отката данных (нужно хранить версии в отдельной таблице или поле)
        tender.version = version
        db.commit()
        return jsonify({"message": "Tender rolled back to version " + str(version)}), 200
    return jsonify({"error": "Unable to rollback tender"}), 404

# Создание нового предложения (bid)
@app.route('/api/bids/new', methods=['POST'])
def create_bid():
    data = request.json
    db: Session = SessionLocal()
    new_bid = Bid(
        name=data['name'],
        description=data.get('description'),
        tender_id=data['tenderId'],
        organization_id=data['organizationId']
    )
    db.add(new_bid)
    db.commit()
    return jsonify({
        "id": new_bid.id,
        "name": new_bid.name,
        "description": new_bid.description,
        "tender_id": new_bid.tender_id,
        "organization_id": new_bid.organization_id,
        "version": new_bid.version
    }), 200

# Публикация предложения
@app.route('/api/bids/<int:bid_id>/publish', methods=['POST'])
def publish_bid(bid_id):
    db: Session = SessionLocal()
    bid = db.query(Bid).filter(Bid.id == bid_id).first()
    if bid and bid.status == BidStatus.CREATED:
        bid.status = BidStatus.PUBLISHED
        db.commit()
        return jsonify({"message": "Bid published"}), 200
    return jsonify({"error": "Bid not found or already published"}), 404

# Редактирование предложения
@app.route('/api/bids/<int:bid_id>/edit', methods=['PATCH'])
def edit_bid(bid_id):
    data = request.json
    db: Session = SessionLocal()
    bid = db.query(Bid).filter(Bid.id == bid_id).first()
    if bid:
        bid.name = data.get('name', bid.name)
        bid.description = data.get('description', bid.description)
        bid.version += 1
        db.commit()
        return jsonify({
            "id": bid.id,
            "name": bid.name,
            "description": bid.description,
            "version": bid.version
        }), 200
    return jsonify({"error": "Bid not found"}), 404

# Откат версии предложения
@app.route('/api/bids/<int:bid_id>/rollback/<int:version>', methods=['PUT'])
def rollback_bid(bid_id, version):
    db: Session = SessionLocal()
    bid = db.query(Bid).filter(Bid.id == bid_id).first()
    if bid and bid.version > version:
        # Логика отката данных (нужно хранить версии)
        bid.version = version
        db.commit()
        return jsonify({"message": "Bid rolled back to version " + str(version)}), 200
    return jsonify({"error": "Unable to rollback bid"}), 404

# Согласование или отклонение предложения
@app.route('/api/bids/<int:bid_id>/decision', methods=['POST'])
def decision_bid(bid_id):
    data = request.json
    decision = data['decision']  # "accept" или "reject"
    db: Session = SessionLocal()
    
    bid = db.query(Bid).filter(Bid.id == bid_id).first()
    if not bid:
        return jsonify({"error": "Bid not found"}), 404
    
    # Проверка кворума (пример с тремя ответственными лицами)
    responsible_count = 3
    quorum = min(3, responsible_count)
    
    if decision == "reject":
        bid.status = BidStatus.CANCELED
        db.commit()
        return jsonify({"message": "Bid rejected"}), 200
    elif decision == "accept" and quorum >= 3:
        bid.status = BidStatus.PUBLISHED
        db.commit()
        return jsonify({"message": "Bid accepted"}), 200
    
    return jsonify({"error": "Decision failed, quorum not reached"}), 400

# Инициализация базы данных и запуск приложения
if __name__ == '__main__':
    init_db()  # Создание таблиц при первом запуске
    app.run(host='0.0.0.0', port=8080)
