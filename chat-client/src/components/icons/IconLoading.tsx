import React from 'react'

interface Props {
	classNames?: string
}

const IconLoading: React.FC<Props> = ({ classNames = '' }) => {
	return (
		<div
			className={`inline-flex h-8 flex-none items-center gap-1 ${classNames}`}
		>
			<div
				className='h-1 w-1 flex-none animate-bounce rounded-full bg-gray-500 dark:bg-gray-400'
				style={{ animationDelay: '0.25s' }}
			></div>
			<div
				className='h-1 w-1 flex-none animate-bounce rounded-full bg-gray-500 dark:bg-gray-400'
				style={{ animationDelay: '0.5s' }}
			></div>
			<div
				className='h-1 w-1 flex-none animate-bounce rounded-full bg-gray-500 dark:bg-gray-400'
				style={{ animationDelay: '0.75s' }}
			></div>
		</div>
	)
}

export default IconLoading
