import { useNavigate } from 'react-router-dom'

const TopBar = () => {
    const navigate = useNavigate()

    return (
        <div className="top-bar">
            UC San Diego - Ideker Lab
            <button
                className="home-button"
                onClick={() => navigate(`/`)}
            >
                <i className="fa-solid fa-house-chimney"></i> Home
            </button>
        </div>
    )
}

export default TopBar