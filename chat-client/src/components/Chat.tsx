import React, { useState, useEffect } from 'react'
import { getChatCompletions } from '../api/api'

interface ChatProps {
	fileId: string
}

const Chat = ({ fileId }: ChatProps) => {
	const [messages, setMessages] = useState<
		{ role: string; content: string }[]
	>([])
	const [input, setInput] = useState('')
	const [isLoading, setIsLoading] = useState(false)

	const handleSendMessage = async () => {
		const newMessage = { role: 'user', content: input }
		setMessages([...messages, newMessage])
		setInput('')
		setIsLoading(true)

		try {
			const response = await getChatCompletions([...messages, newMessage])
			setMessages(prevMessages => [
				...prevMessages,
				{
					role: 'assistant',
					content: response.data.choices[0].message.content,
				},
			])
		} catch (error) {
			console.error('Error fetching chat completion', error)
		} finally {
			setIsLoading(false)
		}
	}

	return (
		<div className='flex flex-col h-full'>
			<div className='flex-grow overflow-auto p-4'>
				{messages.map((msg, index) => (
					<div
						key={index}
						className={
							msg.role === 'user' ? 'text-right' : 'text-left'
						}
					>
						<div
							className={
								msg.role === 'user'
									? 'bg-blue-500 text-white'
									: 'bg-gray-200'
							}
						>
							{msg.content}
						</div>
					</div>
				))}
			</div>
			<div className='p-4'>
				<textarea
					value={input}
					onChange={e => setInput(e.target.value)}
					className='w-full p-2 border border-gray-300'
					rows={3}
				/>
				<button
					onClick={handleSendMessage}
					disabled={isLoading}
					className='w-full mt-2 bg-blue-500 text-white p-2'
				>
					{isLoading ? 'Sending...' : 'Send'}
				</button>
			</div>
		</div>
	)
}

export default Chat
