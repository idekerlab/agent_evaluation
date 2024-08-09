import Draggable from 'react-draggable'
import { ResizableBox } from 'react-resizable'

const FriendlyIFrame = ({ iframeSrc, closeIframe, ...props }) => {
    
    return (
        <Draggable handle=".drag-handle">
            <div
                style={{
                    position: 'fixed',
                    top: '10%',
                    left: '10%',
                    zIndex: 1000,
                    boxShadow: '0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)',
                    backgroundColor: 'white',
                    borderRadius: '10px',
                    overflow: 'hidden',
                    transform: 'scale(1.05)',
                    transition: 'transform 0.0s ease-out'
                }}
            >
                <div style={{ width: '100%', height: '100%', position: 'relative' }}>
                    <div
                        className="drag-handle"
                        style={{
                            width: '100%',
                            height: '30px',
                            cursor: 'move',
                            backgroundColor: '#f0f0f0',
                            borderBottom: '1px solid #ccc',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '0 10px'
                        }}
                    >
                        <span>
                            <i className="fa-solid fa-up-down-left-right fa-lg"></i>
                            <a href={iframeSrc} style={{color: "blue", marginLeft: "10px"}} target='_blank'>
                                <i className="fa-solid fa-arrow-up-right-from-square fa-lg" ></i>
                            </a>
                        </span>
                        <button
                            onClick={closeIframe}
                            className='button'
                            style={{
                                backgroundColor: 'red',
                                color: 'white',
                                marginRight: '10px'
                            }}
                        >
                            <i className="fa-solid fa-xmark fa-xl"></i>
                        </button>
                    </div>
                    <ResizableBox
                        width={600}
                        height={400}
                        minConstraints={[300, 200]}
                        maxConstraints={[1000, 800]}
                        style={{ width: '100%', height: 'calc(100% - 30px)', position: 'relative' }}
                        handle={
                            <span
                                className="resizable-handle"
                                style={{
                                    width: '25px',
                                    height: '25px',
                                    position: 'absolute',
                                    bottom: '0',
                                    right: '0',
                                    cursor: 'se-resize',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    backgroundColor: '#f0f0f0',
                                    borderRadius: '5px'
                                }}
                            >
                                <i className="fa-solid fa-up-right-and-down-left-from-center fa-flip-horizontal fa-lg"></i>
                            </span>
                        }
                    >
                        <iframe
                            src={iframeSrc}
                            style={{ width: '100%', height: '100%', borderRadius: '0 0 10px 10px', pointerEvents: 'auto' }}
                        ></iframe>
                    </ResizableBox>
                </div>
            </div>
        </Draggable>
    )
}

export default FriendlyIFrame
