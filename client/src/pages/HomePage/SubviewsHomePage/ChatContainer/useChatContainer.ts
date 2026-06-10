// Placeholder data — replace with API/WebSocket once social endpoints exist
import { useEffect, useState } from 'react'
import { getFriends } from '../../../../api/socialsWrapper'

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



export interface PublicUser {
    id: number
    username: string
    avatar: string | null
}

export interface Friendship {
    friend: PublicUser
    created_at: string
}


export function useChatContainer() {
    const [friendsList, setFriendsList] = useState<Friendship[]>([])
    const [activeId, setActiveId] = useState<number>(0)
    const [refreshTab, setRefreshTab] = useState(0)

    useEffect(() => {
        getFriends().then(data => setFriendsList(Array.isArray(data) ? data : (data.results ?? [])))
    }, [refreshTab])


    const activeConversation = friendsList.find(f => f.friend.id === activeId) ?? friendsList[0]

    const handleSend = () => {
        // TODO: send via WebSocket
        // setDraft('setActiveId')
    }

    const handleChooseTab = (id: number) => {
        setActiveId(id)
    }

    return { friendsList, activeConversation, activeId, setActiveId, handleChooseTab  }
}
