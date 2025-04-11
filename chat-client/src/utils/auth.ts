const EDUC_USER = 'educ_user'

export const setUser = (email: string, token: string) => {
	const user = {
		email,
		token,
	}
	localStorage.setItem(EDUC_USER, JSON.stringify(user))
}

export const getUser = () => {
	const user = localStorage.getItem(EDUC_USER)
	return user ? JSON.parse(user) : null
}

export const removeUser = () => {
	localStorage.removeItem(EDUC_USER)
}
