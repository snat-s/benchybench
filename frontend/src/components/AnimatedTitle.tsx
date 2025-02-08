'use client'

import Link from 'next/link'

export default function AnimatedTitle() {
  return (
    <>
      <Link href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
        <div className="font-mono flex items-center justify-center gap-20">
          <div className="snake-left" style={{ fontSize: "20px" }}>
            ~~~&gt;
          </div>
          <h1 style={{ textAlign: "center" }}>SNAKEBENCH</h1>
          <div className="snake-right" style={{ fontSize: "20px" }}>
            &lt;~~~
          </div>
        </div>
      </Link>
      <style jsx>{`
        @keyframes crawlLeft {
          0% { transform: translateX(10px); }
          50% { transform: translateX(-10px); }
          100% { transform: translateX(10px); }
        }
        @keyframes crawlRight {
          0% { transform: translateX(-10px); }
          50% { transform: translateX(10px); }
          100% { transform: translateX(-10px); }
        }
        .snake-left {
          animation: crawlLeft 2s infinite ease-in-out;
        }
        .snake-right {
          animation: crawlRight 2s infinite ease-in-out;
        }
      `}</style>
    </>
  )
}