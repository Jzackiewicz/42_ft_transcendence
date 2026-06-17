import { useEffect, useRef, useState } from 'react'
import { deleteFromFriends } from '../../../../../../api/socialsWrapper'
import { useFriendsContext } from '../../../../../../context/FriendsListContext'

export function useFriendsListTabView() {
    const { friendsList, refresh } = useFriendsContext()
    const [error, setError] = useState<string | null>(null)
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    useEffect(() => {
        refresh()
    }, [])

    const handleRemove = async (userId: number) => {
        try {
            await deleteFromFriends(userId)
            refresh()
        } catch {
            clearTimeout(timerRef.current ?? undefined)
            setError('Error during update, try one more time')
            timerRef.current = setTimeout(() => setError(null), 3000)
        }
    }

    return { friendsList, handleRemove, error }
}
