import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useFocusEffect } from 'expo-router';
import api from '@/services/api';
import { WS_BASE_URL } from '@/services/api';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/context/auth-context';

type ChatRoom = {
  id: number;
  doctor_id: number;
  patient_id: number;
  doctor_username: string;
  patient_username: string;
};

type Message = {
  id: number;
  sender_id: number;
  content: string;
  timestamp: string;
  is_read: boolean;
};

export default function ChatScreen() {
  const colorScheme = useColorScheme() ?? 'light';
  const colors = Colors[colorScheme];
  const { user, token } = useAuth();
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRoom, setSelectedRoom] = useState<ChatRoom | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [doctors, setDoctors] = useState<{ id: number; username: string }[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const flatListRef = useRef<FlatList>(null);

  const fetchRooms = async () => {
    try {
      const res = await api.get('/chat/rooms');
      setRooms(res.data);
    } catch {
      Alert.alert('Error', 'No se pudieron cargar las conversaciones');
    } finally {
      setLoading(false);
    }
  };

  const fetchDoctors = async () => {
    try {
      const res = await api.get('/chat/doctors');
      setDoctors(res.data);
    } catch {
      // ignore
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchRooms();
      if (user?.role === 'patient') fetchDoctors();
    }, [])
  );

  // Connect / disconnect WebSocket when selectedRoom changes
  useEffect(() => {
    if (!selectedRoom || !token) return;

    const ws = new WebSocket(`${WS_BASE_URL}/chat/ws/${selectedRoom.id}?token=${token}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const msg: Message = JSON.parse(event.data);
      setMessages((prev) => {
        if (prev.some((m) => m.id === msg.id)) return prev;
        return [...prev, msg];
      });
      setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100);
    };

    ws.onerror = () => {
      // Silent — fallback to REST still works
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [selectedRoom, token]);

  const openRoom = async (room: ChatRoom) => {
    setSelectedRoom(room);
    try {
      const res = await api.get(`/chat/rooms/${room.id}/messages`);
      setMessages(res.data);
    } catch {
      Alert.alert('Error', 'No se pudieron cargar los mensajes');
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedRoom) return;
    const content = newMessage.trim();
    setNewMessage('');

    // Send via WebSocket if connected
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ content }));
    } else {
      // Fallback to REST
      try {
        const res = await api.post(`/chat/rooms/${selectedRoom.id}/messages`, { content });
        setMessages((prev) => [...prev, res.data]);
      } catch {
        Alert.alert('Error', 'No se pudo enviar el mensaje');
      }
    }
  };

  const startChat = async (doctorId: number) => {
    try {
      const res = await api.post(`/chat/rooms/${doctorId}`);
      await fetchRooms();
      openRoom(res.data);
    } catch {
      Alert.alert('Error', 'No se pudo crear la conversación');
    }
  };

  if (loading) {
    return (
      <View style={[styles.center, { backgroundColor: colors.background }]}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  // Chat conversation view
  if (selectedRoom) {
    const otherName =
      user?.id === selectedRoom.doctor_id
        ? selectedRoom.patient_username
        : selectedRoom.doctor_username;

    return (
      <KeyboardAvoidingView
        style={[styles.container, { backgroundColor: colors.background }]}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={90}
      >
        <View style={[styles.chatHeader, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <TouchableOpacity onPress={() => setSelectedRoom(null)}>
            <Text style={[styles.backBtn, { color: colors.primary }]}>← Atrás</Text>
          </TouchableOpacity>
          <Text style={[styles.chatTitle, { color: colors.text }]}>{otherName}</Text>
        </View>

        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.messageList}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: false })}
          renderItem={({ item }) => {
            const isMe = item.sender_id === user?.id;
            return (
              <View
                style={[
                  styles.messageBubble,
                  isMe
                    ? { backgroundColor: colors.primary, alignSelf: 'flex-end' }
                    : { backgroundColor: colors.card, alignSelf: 'flex-start', borderWidth: 1, borderColor: colors.border },
                ]}
              >
                <Text style={[styles.messageText, { color: isMe ? '#fff' : colors.text }]}>
                  {item.content}
                </Text>
                <Text style={[styles.messageTime, { color: isMe ? 'rgba(255,255,255,0.7)' : colors.icon }]}>
                  {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Text>
              </View>
            );
          }}
        />

        <View style={[styles.inputBar, { backgroundColor: colors.card, borderColor: colors.border }]}>
          <TextInput
            style={[styles.messageInput, { color: colors.text, backgroundColor: colors.background, borderColor: colors.border }]}
            placeholder="Escribe un mensaje..."
            placeholderTextColor={colors.icon}
            value={newMessage}
            onChangeText={setNewMessage}
            onSubmitEditing={sendMessage}
            returnKeyType="send"
            blurOnSubmit={false}
          />
          <TouchableOpacity style={[styles.sendBtn, { backgroundColor: colors.primary }]} onPress={sendMessage}>
            <Text style={styles.sendBtnText}>Enviar</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    );
  }

  // Room list view
  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <Text style={[styles.title, { color: colors.text, paddingHorizontal: 20, paddingTop: 60 }]}>
        Chat
      </Text>

      {user?.role === 'patient' && doctors.length > 0 && (
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.icon }]}>Doctores disponibles</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.doctorList}>
            {doctors.map((d) => (
              <TouchableOpacity
                key={d.id}
                style={[styles.doctorCard, { backgroundColor: colors.card, borderColor: colors.border }]}
                onPress={() => startChat(d.id)}
              >
                <Text style={[styles.doctorName, { color: colors.primary }]}>🩺 {d.username}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}

      <ScrollView style={styles.list}>
        {rooms.length === 0 ? (
          <Text style={[styles.empty, { color: colors.icon }]}>
            No tienes conversaciones aún.
          </Text>
        ) : (
          rooms.map((r) => {
            const otherName =
              user?.id === r.doctor_id ? r.patient_username : r.doctor_username;
            const roleLabel = user?.id === r.doctor_id ? 'Paciente' : 'Doctor';
            return (
              <TouchableOpacity
                key={r.id}
                style={[styles.roomCard, { backgroundColor: colors.card, borderColor: colors.border }]}
                onPress={() => openRoom(r)}
              >
                <Text style={[styles.roomName, { color: colors.text }]}>{otherName}</Text>
                <Text style={[styles.roomRole, { color: colors.icon }]}>{roleLabel}</Text>
              </TouchableOpacity>
            );
          })
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 28, fontWeight: 'bold', marginBottom: 16 },
  section: { paddingHorizontal: 20, marginBottom: 16 },
  sectionTitle: { fontSize: 14, fontWeight: '600', marginBottom: 8 },
  doctorList: { gap: 10 },
  doctorCard: { borderRadius: 12, padding: 12, borderWidth: 1 },
  doctorName: { fontWeight: '600', fontSize: 14 },
  list: { paddingHorizontal: 20 },
  empty: { textAlign: 'center', marginTop: 40, fontSize: 16 },
  roomCard: { borderRadius: 16, padding: 16, marginBottom: 10, borderWidth: 1, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  roomName: { fontSize: 16, fontWeight: '700' },
  roomRole: { fontSize: 12 },
  // Chat view
  chatHeader: { flexDirection: 'row', alignItems: 'center', gap: 16, paddingTop: 60, paddingHorizontal: 20, paddingBottom: 12, borderBottomWidth: 1 },
  backBtn: { fontSize: 16, fontWeight: '600' },
  chatTitle: { fontSize: 18, fontWeight: '700' },
  messageList: { padding: 16, gap: 8 },
  messageBubble: { maxWidth: '75%', borderRadius: 16, padding: 12, marginBottom: 4 },
  messageText: { fontSize: 15 },
  messageTime: { fontSize: 11, marginTop: 4, textAlign: 'right' },
  inputBar: { flexDirection: 'row', padding: 12, gap: 8, borderTopWidth: 1 },
  messageInput: { flex: 1, borderWidth: 1, borderRadius: 20, paddingHorizontal: 16, paddingVertical: 10, fontSize: 15 },
  sendBtn: { borderRadius: 20, paddingHorizontal: 20, justifyContent: 'center' },
  sendBtnText: { color: '#fff', fontWeight: '700' },
});
