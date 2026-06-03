import { useState } from 'react'

export type FriendsTab = 'friends' | 'requests' | 'find'

export interface Friend {
    id: number
    username: string
    online: boolean
}

export interface FriendRequest {
    id: number
    username: string
}

export function useFriendsView() {
    const [activeTab, setActiveTab] = useState<FriendsTab>('friends')
    const [searchQuery, setSearchQuery] = useState('')

    const friends: Friend[] = [
        { id: 1, username: 'Vega',   online: true  },
        { id: 2, username: 'Orion',  online: true  },
        { id: 3, username: 'Nova',   online: false },
        { id: 4, username: 'Julia',  online: true  },
        { id: 5, username: 'Aurora', online: false },
        
        { id: 1, username: 'Vega',   online: true  },
        { id: 2, username: 'Orion',  online: true  },
        { id: 3, username: 'Nova',   online: false },
        { id: 4, username: 'Julia',  online: true  },
        { id: 5, username: 'Aurora', online: false },
        { id: 1, username: 'Vega',   online: true  },
        { id: 2, username: 'Orion',  online: true  },
        { id: 3, username: 'Nova',   online: false },
        { id: 4, username: 'Julia',  online: true  },
        { id: 5, username: 'Aurora', online: false },
    ]

    const requests: FriendRequest[] = [
        { id: 1, username: 'Luna'   },
        { id: 2, username: 'Cosmos' },
        { id: 1, username: 'Luna'   },
        { id: 2, username: 'Cosmos' },
        { id: 1, username: 'Luna'   },
        { id: 2, username: 'Cosmos' },
    ]

    const handleRemove    = (id: number)     => { console.log('remove',   id) }
    const handleAccept    = (id: number)     => { console.log('accept',   id) }
    const handleDecline   = (id: number)     => { console.log('decline',  id) }
    const handleSendRequest = (username: string) => { console.log('request', username) }

    return {
        activeTab, setActiveTab,
        friends,
        requests,
        searchQuery, setSearchQuery,
        handleRemove, handleAccept, handleDecline, handleSendRequest,
    }
}
