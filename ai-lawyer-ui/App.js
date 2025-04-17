import React, { useState, useRef } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Dimensions,
  Animated,
  Pressable,
} from 'react-native';

export default function App() {
  const [messages, setMessages] = useState([
    { id: '1', text: '안녕하세요 법률 챗봇입니다.', from: 'bot' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const slideAnim = useRef(new Animated.Value(Dimensions.get('window').width)).current;
  const [panelOpen, setPanelOpen] = useState(false);

  const openPanel = () => {
    setPanelOpen(true);
    Animated.timing(slideAnim, {
      toValue: Dimensions.get('window').width * 0.4,
      duration: 300,
      useNativeDriver: false,
    }).start();
  };

  const closePanel = () => {
    Animated.timing(slideAnim, {
      toValue: Dimensions.get('window').width,
      duration: 300,
      useNativeDriver: false,
    }).start(() => {
      setPanelOpen(false);
    });
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      text: input,
      from: 'user',
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // ✅ 응답 중 메시지 추가
    const loadingMessage = {
      id: 'loading',
      text: '응답 중...',
      from: 'bot',
    };
    setMessages(prev => [...prev, loadingMessage]);


    //여기서 ip넣기
    try {
      const response = await fetch('http://192.168.3.161:8001/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: input, top_k: 3 }),
      });

      const data = await response.json();

      // ✅ 응답 중 메시지 제거
      setMessages(prev => prev.filter(msg => msg.id !== 'loading'));

      const botReply = {
        id: (Date.now() + 1).toString(),
        text: data.answer || '응답이 없습니다.',
        from: 'bot',
      };

      setMessages(prev => [...prev, botReply]);
    } catch (err) {
      setMessages(prev => prev.filter(msg => msg.id !== 'loading'));

      const errorReply = {
        id: (Date.now() + 2).toString(),
        text: 'api 연결 전',
        from: 'bot',
      };
      setMessages(prev => [...prev, errorReply]);
    }

    setLoading(false);
  };

  const renderItem = ({ item }) => (
    <View
      style={[
        styles.messageBubble,
        item.from === 'user' ? styles.userBubble : styles.botBubble,
      ]}
    >
      <Text style={styles.messageText}>{item.text}</Text>
    </View>
  );

  const userQuestions = messages.filter(msg => msg.from === 'user');

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={openPanel}>
          <Text style={styles.menuButton}>≡</Text>
        </TouchableOpacity>
        <Text style={styles.title}>법률 챗봇</Text>
      </View>

      <FlatList
        data={messages}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.chatContainer}
      />

      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={input}
            onChangeText={setInput}
            placeholder="메시지를 입력하세요"
          />
          <TouchableOpacity
            style={[styles.sendButton, loading && { backgroundColor: '#ccc' }]}
            onPress={handleSend}
            disabled={loading}
          >
            <Text style={styles.sendText}>{loading ? '...' : '보내기'}</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>

      {panelOpen && (
        <View style={styles.overlay}>
          <Pressable style={styles.overlayBackground} onPress={closePanel} />
          <Animated.View style={[styles.panel, { left: slideAnim }]}>
            <View style={styles.panelHeader}>
              <Text style={styles.panelTitle}>📌 최근 질문</Text>
              <TouchableOpacity onPress={closePanel}>
                <Text style={styles.closeButton}>닫기</Text>
              </TouchableOpacity>
            </View>
            {userQuestions.length === 0 ? (
              <Text style={{ padding: 10 }}>아직 질문이 없습니다.</Text>
            ) : (
              userQuestions.map((q, i) => (
                <Text key={q.id} style={styles.panelText}>{i + 1}. {q.text}</Text>
              ))
            )}
          </Animated.View>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  chatContainer: { padding: 10 },
  messageBubble: {
    padding: 10,
    marginVertical: 5,
    borderRadius: 15,
    maxWidth: '80%',
  },
  userBubble: {
    backgroundColor: '#DCF8C6',
    alignSelf: 'flex-end',
  },
  botBubble: {
    backgroundColor: '#ECECEC',
    alignSelf: 'flex-start',
  },
  messageText: {
    fontSize: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    borderTopWidth: 1,
    borderColor: '#eee',
    backgroundColor: '#fafafa',
  },
  input: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 10,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  sendButton: {
    marginLeft: 10,
    backgroundColor: '#4e8cff',
    borderRadius: 20,
    paddingVertical: 10,
    paddingHorizontal: 15,
    justifyContent: 'center',
  },
  sendText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  header: {
    paddingHorizontal: 15,
    paddingVertical: 10,
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderColor: '#eee',
  },
  menuButton: {
    fontSize: 24,
    marginRight: 10,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    right: 0,
    left: 0,
    flexDirection: 'row',
    zIndex: 100,
  },
  overlayBackground: {
    flex: 0.4,
    backgroundColor: 'rgba(0,0,0,0.3)',
  },
  panel: {
    width: '60%',
    backgroundColor: '#fff',
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: -2, height: 0 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 5,
  },
  panelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
    borderBottomWidth: 1,
    borderColor: '#eee',
    paddingBottom: 10,
  },
  panelTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  closeButton: {
    fontSize: 16,
    color: '#4e8cff',
  },
  panelText: {
    fontSize: 15,
    marginBottom: 10,
  },
});
