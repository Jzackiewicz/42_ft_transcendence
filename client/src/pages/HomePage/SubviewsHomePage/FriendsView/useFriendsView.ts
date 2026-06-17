import { useState } from 'react'

export type FriendsTab = 'friends' | 'requests' | 'find'

export function useFriendsView() {
    const [activeTab, setActiveTab] = useState<FriendsTab>('friends')

    return { activeTab, setActiveTab }
}
