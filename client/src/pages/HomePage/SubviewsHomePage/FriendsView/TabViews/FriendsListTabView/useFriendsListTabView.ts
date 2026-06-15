import { deleteFromFriends } from '../../../../../../api/socialsWrapper'
import { useFriendsContext } from '../../../../../../context/FriendsListContext'

export function useFriendsListTabView() {
    const { friendsList, refresh } = useFriendsContext()

    const handleRemove = async (userId: number) => {
        await deleteFromFriends(userId)
        refresh()
    }

    return { friendsList, handleRemove }
}
