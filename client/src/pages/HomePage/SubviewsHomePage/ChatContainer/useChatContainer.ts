import { useState } from 'react'

export interface Message {
    id:        number
    from:      'me' | 'them'
    text:      string
    timestamp: string
}

export interface Conversation {
    id:       number
    username: string
    initial:  string
    color:    string
    lastMsg:  string
    unread:   number
    messages: Message[]
}

// Placeholder data — replace with API/WebSocket once social endpoints exist
const MOCK_CONVERSATIONS: Conversation[] = [
    {
        id: 1, username: 'Marek', initial: 'M',
        color: 'linear-gradient(135deg,#00e5ff,#0088aa)',
        lastMsg: 'Good game! 🎮', unread: 2,
        messages: [
            { id: 1, from: 'them', text: 'Hey, wanna play?',      timestamp: '14:20' },
            { id: 2, from: 'me',   text: 'Sure, in 5 min!',       timestamp: '14:21' },
            { id: 3, from: 'them', text: 'Good game! 🎮',         timestamp: '14:45' },
        ],
    },
    {
        id: 2, username: 'Viktoria', initial: 'V',
        color: 'linear-gradient(135deg,#e040fb,#880088)',
        lastMsg: 'rematch?', unread: 0,
        messages: [
            { id: 1, from: 'them', text: 'that was close 😅',     timestamp: '13:10' },
            { id: 2, from: 'me',   text: 'lol you got lucky',      timestamp: '13:11' },
            { id: 3, from: 'them', text: 'rematch?',               timestamp: '13:12' },
        ],
    },
    {
        id: 3, username: 'Jonas', initial: 'J',
        color: 'linear-gradient(135deg,#ffc400,#e65100)',
        lastMsg: 'gg wp', unread: 0,
        messages: [
            { id: 1, from: 'me',   text: 'nice answers bro',       timestamp: '12:00' },
            { id: 2, from: 'them', text: 'gg wp',                  timestamp: '12:01' },
        ],
    },
]

function getConversations(): Conversation[] {
    return MOCK_CONVERSATIONS
}

export function useChatContainer() {
    const [conversations] = useState<Conversation[]>(getConversations())
    const [activeId, setActiveId] = useState<number>(getConversations()[0].id)
    const [draft, setDraft] = useState('')

    const active = conversations.find(c => c.id === activeId) ?? conversations[0]

    const handleSend = () => {
        // TODO: send via WebSocket
        setDraft('')
    }

    return { conversations, active, activeId, setActiveId, draft, setDraft, handleSend }
}
