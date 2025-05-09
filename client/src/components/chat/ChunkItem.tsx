import React, { useState } from 'react'
import { CgFileDocument } from 'react-icons/cg'
import Modal from '../Modal'

interface ChunkItemProps {
	chunks: string[]
}

const ChunkItem: React.FC<ChunkItemProps> = ({ chunks }) => {
	const [showModal, setShowModal] = useState(false)
    const Icon = CgFileDocument as unknown as React.FC

	return (
		<div>
			{showModal && (
				<Modal
					width='max-w-lg'
					isOpen={showModal}
					onClose={() => setShowModal(false)}
				>
					<div className='relative flex h-full w-full flex-col gap-4 p-4'>
						<h3 className='mb-3 pb-2 text-xl font-bold'>
							Найденные фрагменты
						</h3>
						{chunks.map((chunk, index) => (
							<div key={index}>
								<pre
									key={index}
									className='w-full whitespace-pre-wrap break-words p-3 text-sm font-mono'
								>
									{chunk}
								</pre>
								{index < chunks.length - 1 && (
									<hr className='my-4 border-t border-gray-500' />
								)}
							</div>
						))}
					</div>
				</Modal>
			)}
			<div
				onClick={() => setShowModal(true)}
				onKeyDown={e => {
					if (e.key === 'Enter' || e.key === ' ') {
						setShowModal(true)
					}
				}}
				role='button'
				tabIndex={0}
			>
				<div className='group relative flex items-center rounded-xl shadow-sm max-w-72'>
					<div className='flex h-14 w-full items-center gap-2 overflow-hidden rounded-xl border border-gray-200 bg-white p-2 dark:border-gray-800 dark:bg-gray-900'>
						<div className='grid size-10 flex-none place-items-center rounded-lg bg-gray-100 dark:bg-gray-800'>
							<Icon />
						</div>
						<span className='ml-4 items-center text-sm'>
							Фрагменты
						</span>
					</div>
				</div>
			</div>
		</div>
	)
}

export default ChunkItem
