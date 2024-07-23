import StarRating from './StarRating'

const HumanReviewForm = ({review, handleReviewChange, ...props}) => {


    const handleStarChange = (stars) => {
        let newReview = {...review}
        newReview["rating"] = stars
        handleReviewChange(newReview)
    }

    const handleCommentChange = (e) => {
        let newReview = {...review}
        console.log(e.target.value);
        newReview["comments"] = e.target.value
        handleReviewChange(newReview)
    }

    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <StarRating rating={review.rating} setRating={(stars) => handleStarChange(stars)} totalStars={5} />
            <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                <label htmlFor="comments">Comments</label>
                <textarea
                    id="comments"
                    name={'comments'}
                    value={review.comments}
                    onChange={handleCommentChange}
                    style={{ width: '70%', maxWidth:"800px",  padding: '5px', boxSizing: "border-box" }}
                />
            </div>
        </div>
    )
}

export default HumanReviewForm