/**
 * Copyright 2014 Xabier Crespo Álvarez
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @author Xabier Crespo Álvarez (xabicrespog@gmail.com)
 */

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
		localCommand("NotifyEvent", new Commands.NotifyEventCommand());
		localCommand("NotifyMsg", new Commands.NotifyMsgCommand());
	}

	/** Methods that might be called remotely must be public */
	public Commands.NotifyEventResp substraction(int a, int b) {
		int res = a - b;
		System.out.println("I did a substraction: " + a + " - " + b + " = "
				+ res);

		Commands.NotifyEventResp sr = new Commands.NotifyEventResp();
		// sr.total = res;

		return sr;
	}

	// TODO Command response/error handlers	
	/**
	 * Handler for Log in response
	 */
	class LoginRes implements Deferred.Callback<Commands.LoginResp> {
		public Object callback(Commands.LoginResp retval) {

			System.out.println("Log in result" + retval.getResponse());
			return null;
		}
	}

	/**
	 * Handler for Log in error
	 */
	class LoginErr implements Deferred.Callback<Deferred.Failure> {
		public Object callback(Deferred.Failure err) {
			System.out.println("Error during client log in");
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

		Commands.LoginParams rp = new Commands.LoginParams(sUsername,
				sPassword);
		Commands.LoginResp cr = new Commands.LoginResp();

		System.out.println("Trying to log in: " + sUsername);
		AMP.RemoteCommand<Commands.LoginResp> remote = new RemoteCommand<Commands.LoginResp>(
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
			X509Certificate caCert = (X509Certificate) cf
					.generateCertificate(is);

			TrustManagerFactory tmf = TrustManagerFactory
					.getInstance(TrustManagerFactory.getDefaultAlgorithm());
			KeyStore ks = KeyStore.getInstance(KeyStore.getDefaultType());
			ks.load(null); // You don't need the KeyStore instance to come from
							// a file.
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
