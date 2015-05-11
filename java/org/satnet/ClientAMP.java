package org.satnet;

import java.io.FileInputStream;
import java.io.InputStream;
import java.security.KeyStore;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;

import com.twistedmatrix.amp.AMP;
import com.twistedmatrix.internet.ClientFactory;
import com.twistedmatrix.internet.Deferred;
import com.twistedmatrix.internet.IConnector;
import com.twistedmatrix.internet.IProtocol;
import com.twistedmatrix.internet.Reactor;

public class ClientAMP extends AMP {
	Reactor _reactor = null;

	public ClientAMP(Reactor reactor) {
		_reactor = reactor;

		/** Define a local method that might be called remotely. */
		localCommand("NotifyEvent", new Prototipes.NotifyEventCommand());
		localCommand("NotifyMsg", new Prototipes.NotifyMsgCommand());
	}

	/** Methods that might be called remotely must be public */
	public Prototipes.NotifyEventResp substraction(int a, int b) {
		int res = a - b;
		System.out.println("I did a substraction: " + a + " - " + b + " = "
				+ res);

		Prototipes.NotifyEventResp sr = new Prototipes.NotifyEventResp();
		//sr.total = res;

		return sr;
	}

	/**
	 * Class that handles the results of a command invoked remotely. The
	 * callback method is called with a populated response class. Returned
	 * object is handed to chained callback if it exists.
	 */
	class LoginRes implements Deferred.Callback<Prototipes.LoginResp> {
		public Object callback(Prototipes.LoginResp retval) {

			System.out.println("Remote did a Login: 5 + 3 = "
					+ retval.getResponse());
			return null;
		}
	}

	/**
	 * Class that handles the problem if a remote command goes awry. The
	 * callback method is called with a populated Failure class. Returned object
	 * is handed to chained errback if it exists.
	 */
	class LoginErr implements Deferred.Callback<Deferred.Failure> {
		public Object callback(Deferred.Failure err) {

			// Class tc = err.trap(Exception.class);
			// System.out.println("error: " + err.get());
			err.get().printStackTrace();
			System.exit(0);

			return null;
		}
	}

	/**
	 * The example the client and server use the same method and classes to
	 * exchange data, but the client initiates this process upon connection
	 */
	@Override
	public void connectionMade() {
		System.out.println("connected");
		String sUsername = "crespo";
		String sPassword = "cre.spo";
		
		Prototipes.LoginParams rp = new Prototipes.LoginParams(sUsername, sPassword);
		Prototipes.LoginResp cr = new Prototipes.LoginResp();

		System.out.println("Trying to log in: " + sUsername);
		AMP.RemoteCommand<Prototipes.LoginResp> remote = new RemoteCommand<Prototipes.LoginResp>(
				"PasswordLogin", rp, cr);
		Deferred dfd = remote.callRemote();
		dfd.addCallback(new LoginRes());
		dfd.addErrback(new LoginErr());
	}

	@Override
	public void connectionLost(Throwable reason) {
		System.out.println("Connection lost: " + reason);
	}

	/** This context validates the server certificate, which is GOOD. */
	private static SSLContext getSecureContext() {
		// The alias/password for localhost.ks is importkey/password

		SSLContext ctx = null;
		try {
			InputStream is = new FileInputStream("src/key/test.crt");
			// You could get a resource as a stream instead.

			CertificateFactory cf = CertificateFactory.getInstance("X.509");
			X509Certificate caCert = (X509Certificate)cf.generateCertificate(is);

			TrustManagerFactory tmf = TrustManagerFactory
			    .getInstance(TrustManagerFactory.getDefaultAlgorithm());
			KeyStore ks = KeyStore.getInstance(KeyStore.getDefaultType());
			ks.load(null); // You don't need the KeyStore instance to come from a file.
			ks.setCertificateEntry("caCert", caCert);

			tmf.init(ks);

			ctx = SSLContext.getInstance("TLS");
			ctx.init(null, tmf.getTrustManagers(), null);
		} catch (Exception e) {
			e.printStackTrace();
		}

		return ctx;
	}

	public static void main(String[] args) throws Throwable {
		final Reactor reactor = Reactor.get();
		reactor.connectSSL("127.0.0.1", 1234, getSecureContext(),
				new ClientFactory() {
					public IProtocol buildProtocol(Object addr) {
						return new ClientAMP(reactor);
					}

					public void clientConnectionFailed(IConnector connector,
							Throwable reason) {
						System.out.println("Connection failed: " + reason);
						System.exit(0);
					}

					@Override
					public void startedConnecting(IConnector connector) {
						System.out.println("Connecting");
					}

					@Override
					public void clientConnectionLost(IConnector connector,
							Throwable reason) {
						System.out.println("Connection lost: " + reason);
					}
				});

		reactor.run();
	}
}
