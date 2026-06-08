import { useState } from 'react'

export interface Friend {
    id: number
    username: string
    online: boolean
}

export function useFriendsListTabView() {
    const [friends] = useState<Friend[]>([
        { id: 1, username: 'Vega',   online: true  },
        { id: 2, username: 'Orion',  online: true  },
        { id: 3, username: 'Nova',   online: false },
        { id: 4, username: 'Julia',  online: true  },
        { id: 5, username: 'Aurora', online: false },
    ])

    const handleRemove = (id: number) => { console.log('remove', id) }

    return { friends, handleRemove }
}
