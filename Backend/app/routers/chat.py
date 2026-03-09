from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app import crud
from app.auth import get_current_user
from app.database import get_db, SessionLocal
from app.models.user import User
from app.schemas.chat import ChatRoomRead, ChatMessageCreate, ChatMessageRead

router = APIRouter(prefix="/chat", tags=["chat"])

# --- REST endpoints ---


@router.get("/rooms", response_model=list[ChatRoomRead])
def list_my_chat_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rooms = crud.chat.get_chat_rooms_for_user(db, current_user.id)
    result = []
    for room in rooms:
        result.append(
            ChatRoomRead(
                id=room.id,
                doctor_id=room.doctor_id,
                patient_id=room.patient_id,
                doctor_username=room.doctor.username,
                patient_username=room.patient.username,
                created_at=room.created_at,
            )
        )
    return result


@router.post("/rooms/{other_user_id}", response_model=ChatRoomRead, status_code=status.HTTP_201_CREATED)
def create_or_get_chat_room(
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    other_user = crud.user.get_user(db, other_user_id)
    if not other_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Determine doctor/patient roles
    if current_user.role == "doctor" and other_user.role == "patient":
        doctor_id, patient_id = current_user.id, other_user.id
    elif current_user.role == "patient" and other_user.role == "doctor":
        doctor_id, patient_id = other_user.id, current_user.id
    else:
        raise HTTPException(status_code=400, detail="El chat debe ser entre un doctor y un paciente")
    room = crud.chat.get_or_create_chat_room(db, doctor_id=doctor_id, patient_id=patient_id)
    return ChatRoomRead(
        id=room.id,
        doctor_id=room.doctor_id,
        patient_id=room.patient_id,
        doctor_username=room.doctor.username,
        patient_username=room.patient.username,
        created_at=room.created_at,
    )


@router.get("/rooms/{room_id}/messages", response_model=list[ChatMessageRead])
def list_messages(
    room_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify user belongs to this room
    rooms = crud.chat.get_chat_rooms_for_user(db, current_user.id)
    if not any(r.id == room_id for r in rooms):
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sala")
    crud.chat.mark_messages_read(db, room_id, current_user.id)
    return crud.chat.get_messages(db, room_id, skip=skip, limit=limit)


@router.post("/rooms/{room_id}/messages", response_model=ChatMessageRead, status_code=status.HTTP_201_CREATED)
def send_message(
    room_id: int,
    message_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rooms = crud.chat.get_chat_rooms_for_user(db, current_user.id)
    if not any(r.id == room_id for r in rooms):
        raise HTTPException(status_code=403, detail="No tienes acceso a esta sala")
    return crud.chat.create_message(db, room_id, sender_id=current_user.id, content=message_data.content)


@router.get("/doctors", response_model=list[dict])
def list_doctors(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doctors = crud.user.get_doctors(db)
    return [{"id": d.id, "username": d.username, "email": d.email} for d in doctors]


# --- WebSocket for real-time chat ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: int):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: int):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)

    async def broadcast(self, room_id: int, message: dict):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/{room_id}")
async def websocket_chat(websocket: WebSocket, room_id: int):
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            sender_id = data.get("sender_id")
            content = data.get("content")
            if sender_id and content:
                db = SessionLocal()
                try:
                    msg = crud.chat.create_message(db, room_id, sender_id=sender_id, content=content)
                    await manager.broadcast(room_id, {
                        "id": msg.id,
                        "chat_room_id": msg.chat_room_id,
                        "sender_id": msg.sender_id,
                        "content": msg.content,
                        "is_read": msg.is_read,
                        "timestamp": msg.timestamp.isoformat(),
                    })
                finally:
                    db.close()
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
