import { writable } from "svelte/store";

export interface User {
	token: string;
	email: string;
}

export const user = writable<User | null>(null);

export const setUser = (newUser: User) => {
	user.set(newUser);
};

export const login = (token: string, email: string) => {
	const newUser: User = { token, email };
	setUser(newUser);
};

export const logout = () => {
	user.set(null);
};
