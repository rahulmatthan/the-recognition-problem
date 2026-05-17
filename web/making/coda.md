Almost every story in the book has a coda, so it makes sense that this "How this Book Was Written" should as well.

Since it took me a little over a week to write a full-fledged book, I thought I'd see how far I could push it. So I decided to extend the project even further by asking Claude to build a choose-your-own-adventure-style version where readers were offered, at different points in the narrative, the option to take an alternative branch if they so chose. This meant that not only could a reader enjoy the story as originally written, but also see what happens when events change, characters make different choices or the world responds is a different way.

To do this, I shifted the project to Claude Code, spinning up 7 agents that allowed me to write 23 branches virtually simultaneously. The 23 additional branches ran to almost 65,000 words, a little shy of the total word count of the book itself. Since I had a much better hang of what I was doing, and since these were just branches running adjacent to the locked-down plot of each short story in the book, it took a small fraction of the time to complete. The branches were built using the same constraints as the canon—every word was written by AI, in this case, even more so.

<figure class="making-figure">
  <p class="figure-label">The Forest Edition</p>
  <div class="fig-stats">
    <div class="fig-stat"><span class="stat-num">23</span><span class="stat-label">branches</span></div>
    <div class="fig-stat"><span class="stat-num">7</span><span class="stat-label">parallel agents</span></div>
    <div class="fig-stat"><span class="stat-num">~65k</span><span class="stat-label">additional words</span></div>
  </div>
  <svg class="fig-tree" viewBox="0 0 600 320" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="margin-top:1.6rem;">
    <line class="tree-trunk" x1="300" y1="20" x2="300" y2="300"/>
    <text class="tree-label canon" x="306" y="18" text-anchor="start">CANON</text>
    <g>
      <circle cx="300" cy="40"  r="2" fill="var(--ink)"/><text class="tree-label" x="316" y="42">Beat 1</text>
      <circle cx="300" cy="68"  r="2" fill="var(--ink)"/><text class="tree-label" x="316" y="70">Beat 2</text>
      <circle cx="300" cy="96"  r="2" fill="var(--ink)"/><text class="tree-label" x="316" y="98">Beat 3</text>
      <circle cx="300" cy="124" r="2" fill="var(--ink)"/><text class="tree-label" x="316" y="126">Beat 4</text>
      <circle cx="300" cy="152" r="2" fill="var(--ink)"/><text class="tree-label" x="316" y="154">Beat 5</text>
      <circle cx="300" cy="180" r="2" fill="var(--ink)"/><text class="tree-label" x="316" y="182">Beat 6</text>
      <circle cx="300" cy="208" r="2" fill="var(--ink)"/><text class="tree-label" x="316" y="210">Beat 7</text>
      <circle cx="300" cy="236" r="2" fill="var(--ink)"/><text class="tree-label" x="316" y="238">Beat 8</text>
      <circle cx="300" cy="264" r="2" fill="var(--ink)"/><text class="tree-label" x="316" y="266">Beat 9</text>
      <circle cx="300" cy="292" r="2" fill="var(--ink)"/><text class="tree-label" x="316" y="294">Beat 10</text>
    </g>
    <path class="tree-branch" d="M 300 40 Q 220 36 140 22"/>
    <path class="tree-branch" d="M 300 40 Q 230 50 150 56"/>
    <path class="tree-branch" d="M 300 68 Q 210 60 110 50"/>
    <path class="tree-branch" d="M 300 68 Q 220 80 130 84"/>
    <path class="tree-branch" d="M 300 96 Q 200 92 100 88"/>
    <path class="tree-branch" d="M 300 96 Q 210 108 120 112"/>
    <path class="tree-branch" d="M 300 124 Q 200 116 90 110"/>
    <path class="tree-branch" d="M 300 124 Q 200 124 80 124"/>
    <path class="tree-branch" d="M 300 124 Q 210 138 110 140"/>
    <path class="tree-branch" d="M 300 152 Q 200 146 80 142"/>
    <path class="tree-branch" d="M 300 152 Q 200 152 70 152"/>
    <path class="tree-branch" d="M 300 152 Q 200 162 90 168"/>
    <path class="tree-branch" d="M 300 180 Q 210 174 110 170"/>
    <path class="tree-branch" d="M 300 180 Q 200 188 90 194"/>
    <path class="tree-branch" d="M 300 208 Q 200 202 90 198"/>
    <path class="tree-branch" d="M 300 208 Q 210 216 110 220"/>
    <path class="tree-branch" d="M 300 236 Q 200 228 90 222"/>
    <path class="tree-branch" d="M 300 236 Q 200 236 70 236"/>
    <path class="tree-branch" d="M 300 236 Q 200 246 100 252"/>
    <path class="tree-branch" d="M 300 264 Q 200 256 90 250"/>
    <path class="tree-branch" d="M 300 264 Q 200 272 100 278"/>
    <path class="tree-branch" d="M 300 292 Q 200 286 100 282"/>
    <path class="tree-branch" d="M 300 292 Q 200 300 90 304"/>
    <text class="tree-label" x="10" y="160" text-anchor="start" style="font-style:italic;">23 branches</text>
  </svg>
  <p class="figure-caption">The canon stays. The branches appear when invited. Each one a story that could have happened instead.</p>
</figure>

I then told Claude Code to build me a website to present the project. I spent some time figuring out how it would look, the animations it would have, and the visual indication readers would get to indicate that they are now on a branch, not the canon. This is what you are reading right now.
