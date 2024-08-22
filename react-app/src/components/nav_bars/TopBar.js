import { useNavigate } from 'react-router-dom'

const TopBar = () => {
    const navigate = useNavigate()

    return (
        <div className="top-bar">
            UC San Diego - Ideker Lab
        </div>
    )
}

export default TopBar