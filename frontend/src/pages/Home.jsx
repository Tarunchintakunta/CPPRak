import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, QrCode, Calendar, CheckCircle, ArrowRight } from 'lucide-react';

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="flex-1">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-secondary/10" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32 relative">
          <div className="text-center max-w-3xl mx-auto">
            <div className="flex justify-center mb-6">
              <div className="w-20 h-20 bg-primary/20 rounded-3xl flex items-center justify-center">
                <Shield className="w-10 h-10 text-primary" />
              </div>
            </div>
            <h1 className="text-5xl sm:text-6xl font-extrabold mb-6 leading-tight">
              Secure Event
              <span className="text-primary"> Ticketing</span>
              <br />with QR Codes
            </h1>
            <p className="text-xl text-text-muted mb-10 leading-relaxed">
              Rakshan provides tamper-proof, cryptographically signed QR tickets for your events.
              Register, get your QR code, and check in seamlessly.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/events" className="inline-flex items-center justify-center gap-2 bg-primary hover:bg-primary-dark text-white font-semibold px-8 py-4 rounded-xl text-lg no-underline transition-colors">
                Browse Events <ArrowRight className="w-5 h-5" />
              </Link>
              {!user && (
                <Link to="/register" className="inline-flex items-center justify-center gap-2 bg-surface-light hover:bg-surface-lighter text-text font-semibold px-8 py-4 rounded-xl text-lg no-underline border border-surface-lighter transition-colors">
                  Create Account
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">How it works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { icon: Calendar, title: 'Browse & Register', desc: 'Find upcoming events and register with a single click.' },
            { icon: QrCode, title: 'Get QR Ticket', desc: 'Receive a cryptographically signed QR code ticket instantly.' },
            { icon: CheckCircle, title: 'Scan & Check In', desc: 'Show your QR code at the venue for instant, secure check-in.' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="bg-surface rounded-2xl p-8 border border-surface-lighter text-center hover:border-primary/40 transition-colors">
              <div className="w-14 h-14 bg-primary/15 rounded-xl flex items-center justify-center mx-auto mb-5">
                <Icon className="w-7 h-7 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">{title}</h3>
              <p className="text-text-muted leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
