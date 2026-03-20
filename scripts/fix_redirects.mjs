import fs from 'fs';

let v = JSON.parse(fs.readFileSync('vercel.json', 'utf8'));

const newRedirects = [
  {
    "source": "/petreceri/animator-(?<char>[^/]+)-petreceri-copii-(?<loc>[^/]+)/?",
    "destination": "/petreceri/animatori-petreceri-copii-$char-$loc",
    "statusCode": 301
  },
  {
    "source": "/petreceri/petrecere-tematica-(?<char>[^/]+)-copii-(?<loc>[^/]+)/?",
    "destination": "/petreceri/animatori-petreceri-copii-$char-$loc",
    "statusCode": 301
  },
  {
    "source": "/wp-admin/(.*)",
    "destination": "/",
    "statusCode": 301
  },
  {
    "source": "/wp-content/(.*)",
    "destination": "/",
    "statusCode": 301
  },
  {
    "source": "/wp-includes/(.*)",
    "destination": "/",
    "statusCode": 301
  },
  {
    "source": "/blog/(.*)",
    "destination": "/",
    "statusCode": 301
  },
  {
    "source": "/blog/?",
    "destination": "/",
    "statusCode": 301
  }
];

v.redirects = [...newRedirects, ...v.redirects];
fs.writeFileSync('vercel.json', JSON.stringify(v, null, 4));
console.log('✅ Vercel JSON updated successfully with WP-admin and Regex catchalls!');
