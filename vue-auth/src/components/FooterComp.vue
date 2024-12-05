<template>
     <footer>
            <div className="footer-content">
                <div className="footer-section">
                    <h3>Use cases</h3>
                    <a href="#">UI design</a>
                    <a href="#">UX design</a>
                    <a href="#">Wireframing</a>
                    <a href="#">Diagramming</a>
                    <a href="#">Brainstorming</a>
                    <a href="#">Online whiteboard</a>
                    <a href="#">Team collaboration</a>
                </div>
                <div className="footer-section">
                    <h3>Explore</h3>
                    <a href="#">Design</a>
                    <a href="#">Prototyping</a>
                    <a href="#">Development features</a>
                    <a href="#">Design systems</a>
                    <a href="#">Collaboration features</a>
                    <a href="#">Design process</a>
                    <a href="#">FigJam</a>
                </div>
                <div className="footer-section">
                    <h3>Resources</h3>
                    <a href="#">Blog</a>
                    <a href="#">Best practices</a>
                    <a href="#">Colors</a>
                    <a href="#">Color wheel</a>
                    <a href="#">Support</a>
                    <a href="#">Developers</a>
                    <a href="#">Resource library</a>
                </div>
            </div>
        </footer>
</template>
<script>
export default{
    name:"FooterComp"
}
</script>
<style>
footer {
    background-color: var(--color-lightblue);
    padding: 30px 20px;
    text-align: center;
    color: #5b4b8a;
    justify-content: center;
    align-items: center;
    display: flex;
}

footer .footer-content {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 50px;
    margin-bottom: 20px;
    max-width: 900px;
}

footer .footer-section {
    flex: 1;
    min-width: 200px;
    padding: 10px;
    text-align: left;
}

footer .footer-section h3 {
    font-size: 1.2em;
    margin-bottom: 10px;
    color: #5b4b8a;
}

footer .footer-section a {
    display: block;
    color: #5b4b8a;
    text-decoration: none;
    margin: 5px 0;
}

footer .footer-section a:hover {
    text-decoration: underline;
}

footer .footer-social {
    margin-top: 20px;
}

footer .footer-social a {
    margin: 0 10px;
    color: #5b4b8a;
    text-decoration: none;
}

footer .footer-social a:hover {
    text-decoration: underline;
}

footer p {
    margin-top: 20px;
    font-size: 0.9em;
}
</style>